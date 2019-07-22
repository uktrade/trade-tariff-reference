from django.shortcuts import redirect, reverse
from django.templatetags import static
from django.views.generic import FormView, RedirectView, TemplateView

from .forms import CreateAgreementForm, ManageExtendedInformationForm


class ManageAgreementScheduleView(TemplateView):
    template_name = 'schedule/manage.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['agreements'] = [
            {
                'id': 'Israel',
                'area_name': 'Israel',
                'country_code': '1L',
                'title': 'Agreement between the United Kingdom of Great Britain and Northern Ireland and Israel',
                'date': '21 February 2019',
                'version': '1.0',
                'download_url': reverse('schedule:download', kwargs={'country': 'israel'}),
                'edit_url': '',
            }
        ]
        return context_data


class DownloadAgreementScheduleView(RedirectView):

    permanent = False
    query_string = False

    def get_redirect_url(self, *args, **kwargs):
        country = kwargs['country']
        return static.static(f'/tariff/documents/{country}_annex.docx')


class CreateAgreementScheduleView(FormView):
    template_name = 'schedule/create.html'
    form_class = CreateAgreementForm

    def form_valid(self, form):
        if form.cleaned_data['extended_information']:
            return redirect(reverse('schedule:manage-extended-info'))
        return redirect(reverse('schedule:manage'))


class ManageExtendedInformationAgreementScheduleView(FormView):
    template_name = 'schedule/manage_extended_information.html'
    form_class = ManageExtendedInformationForm

    def form_valid(self, form):
        return redirect(reverse('schedule:manage'))
