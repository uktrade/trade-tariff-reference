from django.urls import include, path, re_path

from .views import (
    CreateAgreementScheduleView,
    DownloadAgreementScheduleView,
    DownloadMFNScheduleView,
    EditAgreementScheduleView,
    ManageAgreementScheduleView,
    ManageExtendedInformationAgreementScheduleView,
    ManageMFNScheduleView,
    RegenerateAgreementScheduleView,
    RegenerateMFNScheduleView,
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
        'regenerate/<slug:slug>/',
        RegenerateAgreementScheduleView.as_view(),
        name='regenerate',
    ),
    path(
        'edit/<slug:slug>/',
        EditAgreementScheduleView.as_view(),
        name='edit',
    ),

]

mfn_urls = [
    path(
        'manage/',
        ManageMFNScheduleView.as_view(),
        name='manage',
    ),
    path(
        'download/<str:document_type>/',
        DownloadMFNScheduleView.as_view(),
        name='download',
    ),
    re_path(
        'generate/(?P<document_type>schedule|classification)/',
        RegenerateMFNScheduleView.as_view(),
        name='regenerate',
    ),
]

urlpatterns = [
    path('fta/', include((fta_urls, app_name), namespace='fta')),
    path('mfn/', include((mfn_urls, app_name), namespace='mfn')),
]
