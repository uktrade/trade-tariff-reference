from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def tariff_management_url():
    return settings.TARIFF_MANAGEMENT_URL.geturl()
