from django.utils import timezone

import json_log_formatter


class JSONLogFormatter(json_log_formatter.JSONFormatter):

    def json_record(self, message, extra, record):
        extra['message'] = message
        if 'request' in extra:
            request = extra.pop('request')
            if request and request.user.is_authenticated:
                extra['user_id'] = request.user.id
                extra['user_email'] = request.user.email
        if 'time' not in extra:
            extra['time'] = timezone.now()
        return extra
