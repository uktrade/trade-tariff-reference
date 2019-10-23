import time

from django.shortcuts import redirect
from django.urls import resolve
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

import pytz


class HealthCheckMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.start_time = time.time()
        return self.get_response(request)


class TimezoneMiddleware(MiddlewareMixin):

    def process_request(self, request):
        tzname = 'Europe/London'
        timezone.activate(pytz.timezone(tzname))


class ProtectAllViewsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if resolve(request.path).app_name not in ['authbroker_client', 'account'] and not request.user.is_authenticated:
            return redirect('authbroker_client:login')

        return self.get_response(request)
