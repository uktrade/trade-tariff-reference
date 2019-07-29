from django.urls import path

from .views import (
    CreateAgreementScheduleView,
    DownloadAgreementScheduleView,
    EditAgreementScheduleView,
    ManageAgreementScheduleView,
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
        'manage/<slug:slug>/extended-info/',
        ManageExtendedInformationAgreementScheduleView.as_view(),
        name='manage-extended-info',
    ),
    path(
        'manage/',
        ManageAgreementScheduleView.as_view(),
        name='manage',
    ),
    path(
        'download/<slug:slug>/',
        DownloadAgreementScheduleView.as_view(),
        name='download',
    ),
    path(
        'edit/<slug:slug>/',
        EditAgreementScheduleView.as_view(),
        name='edit',
    )
]
