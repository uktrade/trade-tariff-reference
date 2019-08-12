from django.http import HttpResponse
from django.db import transaction, IntegrityError
from django.shortcuts import get_object_or_404, redirect, reverse
from django.views.generic import CreateView, FormView, RedirectView, TemplateView, UpdateView

from .constants import DOCX_CONTENT_TYPE
from .forms import AgreementModelForm, ExtendedQuotaForm, ManageExtendedInformationForm
from .models import Agreement, ExtendedQuota
from .quotas import process_quotas
from .utils import generate_document


class ManageAgreementScheduleView(TemplateView):
    template_name = 'schedule/manage.html'

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
            return redirect(reverse('schedule:manage'))
        response = HttpResponse(agreement.document.read(), content_type=DOCX_CONTENT_TYPE)
        response['Content-Disposition'] = f'inline; filename={agreement.slug}_annex.docx'
        return response


class BaseAgreementScheduleView:
    template_name = 'schedule/create.html'
    form_class = AgreementModelForm

    def get_success_url(self):
        if 'extended_information' in self.request.POST.dict():
            return reverse('schedule:manage-extended-info', kwargs={'slug': self.object.slug})
        generate_document(self.object)
        return reverse('schedule:manage')


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
    template_name = 'schedule/manage_extended_information.html'
    form_class = ManageExtendedInformationForm

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
        if not quota_data:
            return redirect(reverse('schedule:manage'))

        try:
            with transaction.atomic():
                self.delete_quotas(agreement, quota_data)
                errors = self.save_quotas(agreement, quota_data)
                if errors:
                    form.add_error(None, errors)
                    raise IntegrityError('Errors found')

        except IntegrityError:
            return self.form_invalid(form)

        generate_document(agreement)
        return redirect(reverse('schedule:manage'))

    def save_quotas(self, agreement, quota_data):
        errors = {}
        for quota_order_number_id, quota in quota_data.items():
            try:
                instance = ExtendedQuota.objects.get(
                    quota_order_number_id=quota_order_number_id, agreement=agreement
                )
            except:
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
