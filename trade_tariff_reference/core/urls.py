from django.urls import path

from .views import HomepageView, HealthCheckView

app_name = 'core'

urlpatterns = [
    path('', HomepageView.as_view(), name='homepage'),
    path('healthcheck', HealthCheckView.as_view(), name='health-check'),
]
