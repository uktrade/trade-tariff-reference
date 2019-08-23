from django.contrib import admin

from trade_tariff_reference.schedule.models import (
    Agreement,
    Chapter,
    ChapterNote,
    DocumentHistory,
    ExtendedQuota,
    LatinTerm,
    SpecialNote,
)

admin.site.register(Agreement)
admin.site.register(Chapter)
admin.site.register(ChapterNote)
admin.site.register(DocumentHistory)
admin.site.register(ExtendedQuota)
admin.site.register(SpecialNote)
admin.site.register(LatinTerm)
