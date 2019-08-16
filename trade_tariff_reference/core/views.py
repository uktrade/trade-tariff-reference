import time

from django.views.generic import TemplateView


class HomepageView(TemplateView):
    template_name = 'core/index.html'


class HealthCheckView(TemplateView):
    template_name = 'core/healthcheck.html'

    def get_context_data(self, **kwargs):
        """ Adds status and response time to response context"""
        context = super().get_context_data(**kwargs)
        context['status'] = 'OK'
        # nearest approximation of a response time
        context['response_time'] = time.time() - self.request.start_time
        return context
