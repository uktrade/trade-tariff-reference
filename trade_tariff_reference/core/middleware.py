import time

import pytz

from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin


class HealthCheckMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.start_time = time.time()
        return self.get_response(request)


class TimezoneMiddleware(MiddlewareMixin):

    def process_request(self, request):
        tzname = 'Europe/London'
        timezone.activate(pytz.timezone(tzname))
