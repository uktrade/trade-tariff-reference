from django.urls import path

from .views import AgreementViewSet


app_name = 'api'

GET_LIST = {'get': 'list'}

GET_OBJECT = {'get': 'retrieve'}


urlpatterns = [
    path(
        'agreement/',
        AgreementViewSet.as_view(actions=GET_LIST),
        name='agreement-list',
    ),
    path(
        'agreement/<slug:slug>/',
        AgreementViewSet.as_view(actions=GET_OBJECT),
        name='agreement-detail',
    ),
]


