from django.contrib import admin

from trade_tariff_reference.schedule.models import Agreement, DocumentHistory, ExtendedQuota

admin.site.register(Agreement)
admin.site.register(DocumentHistory)
admin.site.register(ExtendedQuota)
