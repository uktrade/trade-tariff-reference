from django.contrib import admin

from trade_tariff_reference.schedule.models import Agreement, DocumentHistory

admin.site.register(Agreement)
admin.site.register(DocumentHistory)
