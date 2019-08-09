from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, reverse
from django.views.generic import CreateView, FormView, RedirectView, TemplateView, UpdateView

from .constants import DOCX_CONTENT_TYPE
from .forms import AgreementModelForm, ExtendedQuotaForm, ManageExtendedInformationForm
from .models import Agreement
from .quotas import process_quotas


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
        if quota_data:
            self.save_quotas(self.get_agreement(), quota_data)
        return redirect(reverse('schedule:manage'))

    def save_quotas(self, agreement, quota_data):
        for quota_order_number_id, quota in quota_data.items():
            quota_form = ExtendedQuotaForm(
                data={
                    'quota_order_number_id': quota_order_number_id,
                    'agreement': agreement.pk,
                    **quota
                }
            )
            if quota_form.is_valid():
                quota_form.save()
            else:
                pass
                # MPP: TODO return an error when a quota has invalid data
