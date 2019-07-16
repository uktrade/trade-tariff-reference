from django.urls import path
from .views import ManageAgreementScheduleView, DownloadAgreementScheduleView

app_name = 'schedule'

urlpatterns = [
    path('manage/', ManageAgreementScheduleView.as_view(), name='manage'),
    path('download/<country>/', DownloadAgreementScheduleView.as_view(), name='download')
]
