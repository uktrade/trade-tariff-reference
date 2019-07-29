from django.shortcuts import redirect, reverse
from django.templatetags import static
from django.views.generic import CreateView, FormView, RedirectView, TemplateView, UpdateView

from .forms import AgreementModelForm, ManageExtendedInformationForm
from .models import Agreement


class ManageAgreementScheduleView(TemplateView):
    template_name = 'schedule/manage.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['agreements'] = Agreement.objects.all().order_by('slug')
        return context_data


class DownloadAgreementScheduleView(RedirectView):

    permanent = False
    query_string = False

    def get_redirect_url(self, *args, **kwargs):
        country = kwargs['country']
        return static.static(f'/tariff/documents/{country}_annex.docx')


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

    def form_valid(self, form):
        return redirect(reverse('schedule:manage'))
