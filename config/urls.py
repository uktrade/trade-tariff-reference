from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('', include('core.urls', namespace='core')),
    path('schedule/', include('schedule.urls', namespace='schedule')),
    path('admin/', admin.site.urls)
]
