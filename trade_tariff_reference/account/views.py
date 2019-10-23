from django.contrib.auth import logout
from django.views.generic import TemplateView


class LogoutView(TemplateView):
    template_name = 'account/logout.html'

    def get(self, request, *args, **kwargs):
        logout(self.request)
        return super().get(request, *args, **kwargs)
