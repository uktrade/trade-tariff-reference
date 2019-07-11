from django.urls import path
from .views import ManageAgreementScheduleView

app_name = 'schedule'

urlpatterns = [
    path('manage/', ManageAgreementScheduleView.as_view(), name='manage'),
]
