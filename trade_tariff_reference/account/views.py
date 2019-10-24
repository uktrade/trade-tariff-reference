from django.contrib.auth import logout
from django.views.generic import TemplateView

# Warning Any views placed in the accounts app are not redirected to the auth broker login page


class LogoutView(TemplateView):
    template_name = 'account/logout.html'

    def get(self, request, *args, **kwargs):
        logout(self.request)
        return super().get(request, *args, **kwargs)
