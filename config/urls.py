from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('', include('trade_tariff_reference.core.urls', namespace='core')),
    path('schedule/', include('trade_tariff_reference.schedule.urls', namespace='schedule')),
    path('admin/', admin.site.urls)
]
