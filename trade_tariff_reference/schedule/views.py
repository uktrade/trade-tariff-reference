import json
import logging

from deepdiff import DeepDiff

from django.db import IntegrityError, transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, reverse
from django.views.generic import CreateView, FormView, RedirectView, TemplateView, UpdateView

from trade_tariff_reference.documents.mfn.constants import CLASSIFICATION, SCHEDULE
from trade_tariff_reference.documents.tasks import generate_fta_document, generate_mfn_master_document

from .constants import DOCX_CONTENT_TYPE
from .forms import AgreementModelForm, ExtendedQuotaForm, ManageExtendedInformationForm
from .models import Agreement, ExtendedQuota, MFNDocument
from .quotas import process_quotas
from .utils import generate_document, get_initial_quotas


logger = logging.getLogger(__name__)


class ManageAgreementScheduleView(TemplateView):
    template_name = 'schedule/fta/manage.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['agreements'] = Agreement.objects.all().order_by('slug')
        return context_data


class DownloadAgreementScheduleView(RedirectView):

    def get_agreement(self):
        return get_object_or_404(Agreement, slug=self.kwargs['slug'])

    def get(self, request, *args, **kwargs):
        agreement = self.get_agreement()
        if not agreement.document and agreement.is_document_available:
            return redirect(reverse('schedule:fta:manage'))
        response = HttpResponse(agreement.document.read(), content_type=DOCX_CONTENT_TYPE)
        response['Content-Disposition'] = f'inline; filename={agreement.slug}_annex.docx'
        return response


class RegenerateAgreementScheduleView(RedirectView):

    def get_agreement(self):
        return get_object_or_404(Agreement, slug=self.kwargs['slug'])

    def get(self, request, *args, **kwargs):
        agreement = self.get_agreement()
        if not agreement.is_document_generating:
            generate_fta_document.delay(agreement.slug, force=True)
        return redirect(reverse('schedule:fta:manage'))


class BaseAgreementScheduleView:
    template_name = 'schedule/fta/create.html'
    form_class = AgreementModelForm

    def get_success_url(self):
        if 'extended_information' in self.request.POST.dict():
            return reverse('schedule:fta:manage-extended-info', kwargs={'slug': self.object.slug})
        generate_document(self.object)
        return reverse('schedule:fta:manage')

    def get_form_kwargs(self):
        return {
            'request': self.request,
            **super().get_form_kwargs(),
        }


class CreateAgreementScheduleView(BaseAgreementScheduleView, CreateView):

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['heading'] = 'Create new agreement'
        return context_data


class EditAgreementScheduleView(BaseAgreementScheduleView, UpdateView):
    model = Agreement

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['heading'] = 'Edit agreement'
        return context_data


class ManageExtendedInformationAgreementScheduleView(FormView):
    template_name = 'schedule/fta/manage_extended_information.html'
    form_class = ManageExtendedInformationForm

    def change_dict(self, change_instance):
        if change_instance:
            return get_initial_quotas(change_instance, lst=True)
        return {}

    def log_change(self, initial_change_data, change_data):
        result = DeepDiff(
            initial_change_data,
            change_data,
        )
        result = json.loads(result.to_json())
        if result:
            self._log_message(result)

    def check_for_updates(self, agreement, initial_change_data):
        change_data = self.change_dict(agreement)
        try:
            self.log_change(initial_change_data, change_data)
        except TypeError:
            self._log_message({})

    def _log_message(self, extra):
        extra['request'] = self.request
        agreement = self.get_agreement()
        extra['agreement_id'] = agreement.id
        logger.info('Agreement quotas updated', extra=extra)

    def get_agreement(self):
        return get_object_or_404(Agreement, slug=self.kwargs['slug'])

    def get_form_kwargs(self):
        return {
            'agreement': self.get_agreement(),
            **super().get_form_kwargs(),
        }

    def form_valid(self, form):
        quota_data = process_quotas(form.cleaned_data)
        agreement = self.get_agreement()
        initial_change_data = self.change_dict(agreement)

        if not quota_data:
            return redirect(reverse('schedule:fta:manage'))

        try:
            with transaction.atomic():
                self.delete_quotas(agreement, quota_data)
                errors = self.save_quotas(agreement, quota_data)
                if errors:
                    form.add_error(None, errors)
                    raise IntegrityError('Errors found')

        except IntegrityError:
            return self.form_invalid(form)

        self.check_for_updates(agreement, initial_change_data)
        generate_document(agreement)
        return redirect(reverse('schedule:fta:manage'))

    def save_quotas(self, agreement, quota_data):
        errors = {}
        for quota_order_number_id, quota in quota_data.items():
            try:
                instance = ExtendedQuota.objects.get(
                    quota_order_number_id=quota_order_number_id, agreement=agreement
                )
            except ExtendedQuota.DoesNotExist:
                instance = None
            quota_form = ExtendedQuotaForm(
                data={
                    'quota_order_number_id': quota_order_number_id,
                    'agreement': agreement.pk,
                    'quota_type': ExtendedQuota.FIRST_COME_FIRST_SERVED,
                    **quota
                },
                instance=instance,
            )
            if quota_form.is_valid():
                quota_form.save()
            else:
                if quota.get('quota_type') == ExtendedQuota.LICENSED:
                    errors = self.add_error(errors, 'licensed_quotas', quota_form.errors)
                elif quota.get('scope'):
                    errors = self.add_error(errors, 'scope_quotas', quota_form.errors)
                elif quota.get('addendum'):
                    errors = self.add_error(errors, 'staging_quotas', quota_form.errors)
                else:
                    errors = self.add_error(errors, 'origin_quotas', quota_form.errors)
        return errors

    def add_error(self, error_dict, key, errors):
        if key not in error_dict:
            error_dict[key] = [errors.as_text()]
        else:
            error_dict[key].append(errors.as_text())
        return error_dict

    def delete_quotas(self, agreement, quotas):
        existing_quotas = ExtendedQuota.objects.filter(agreement=agreement)
        deleted_quotas = existing_quotas.exclude(quota_order_number_id__in=quotas.keys())
        deleted_quotas.delete()


class ManageMFNScheduleView(TemplateView):
    template_name = 'schedule/mfn/manage.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['heading'] = 'MFN schedules'
        context_data['schedule_document'] = MFNDocument.objects.filter(document_type=SCHEDULE).first()
        context_data['classification_document'] = MFNDocument.objects.filter(document_type=CLASSIFICATION).first()
        return context_data


class DownloadMFNScheduleView(RedirectView):

    def get_object(self):
        return get_object_or_404(MFNDocument, document_type=self.kwargs['document_type'])

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        if not obj.document:
            return redirect(reverse('schedule:mfn:manage'))
        response = HttpResponse(obj.document.read(), content_type=DOCX_CONTENT_TYPE)
        response['Content-Disposition'] = f'inline; filename={obj.document_type}.docx'
        return response


class RegenerateMFNScheduleView(RedirectView):

    def get_mfn_document(self):
        try:
            return MFNDocument.objects.get(document_type=self.kwargs['document_type'])
        except MFNDocument.DoesNotExist:
            return

    def get(self, request, *args, **kwargs):
        mfn_document = self.get_mfn_document()
        if not mfn_document or not mfn_document.is_document_generating:
            generate_mfn_master_document.delay(self.kwargs['document_type'], force=True)
        return redirect(reverse('schedule:mfn:manage'))
