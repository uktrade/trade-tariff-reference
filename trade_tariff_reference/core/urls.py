from django.urls import path

from .views import HomepageView

app_name = 'core'

urlpatterns = [
    path('', HomepageView.as_view(), name='homepage'),
]
