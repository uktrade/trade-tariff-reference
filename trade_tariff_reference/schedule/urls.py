from django.urls import path
from .views import (
    ManageAgreementScheduleView,
    DownloadAgreementScheduleView,
    CreateAgreementScheduleView,
    ManageExtendedInformationAgreementScheduleView,
)

app_name = 'schedule'

urlpatterns = [
    path(
        'create/',
        CreateAgreementScheduleView.as_view(),
        name='create',
    ),
    path(
        'manage/extended-info/',
        ManageExtendedInformationAgreementScheduleView.as_view(),
        name='manage-extended-info',
    ),
    path(
        'manage/',
        ManageAgreementScheduleView.as_view(),
        name='manage',
    ),
    path(
        'download/<country>/',
        DownloadAgreementScheduleView.as_view(),
        name='download',
        )
]
