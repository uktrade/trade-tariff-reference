from django.urls import include, path

from .views import (
    CreateAgreementScheduleView,
    DownloadAgreementScheduleView,
    EditAgreementScheduleView,
    ManageAgreementScheduleView,
    ManageExtendedInformationAgreementScheduleView,
)

app_name = 'schedule'

fta_urls = [
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

urlpatterns = [
    path('fta/', include((fta_urls, app_name), namespace='fta')),
]