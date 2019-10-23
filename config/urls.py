from django.contrib import admin
from django.urls import include, path

from trade_tariff_reference.core.admin import admin_login_view


urlpatterns = [
    path('', include('trade_tariff_reference.core.urls', namespace='core')),
    path('api/', include('trade_tariff_reference.api.urls', namespace='api')),
    path('documents/', include('trade_tariff_reference.schedule.urls', namespace='schedule')),
    path('auth/', include('authbroker_client.urls', namespace='authbroker')),
    path('admin/login/', admin_login_view),
    path('admin/', admin.site.urls),
    path('u/', include('trade_tariff_reference.account.urls', namespace='account')),
]
