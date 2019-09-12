from django.contrib import admin

from trade_tariff_reference.schedule.models import (
    Agreement,
    AgreementDocumentHistory,
    Chapter,
    ChapterDocumentHistory,
    ChapterNote,
    ExtendedQuota,
    LatinTerm,
    MFNDocument,
    MFNDocumentHistory,
    SpecialNote,
)


class ChapterAdmin(admin.ModelAdmin):
    readonly_fields = [
        'schedule_document_created_at',
        'schedule_document_check_sum',
        'classification_document_created_at',
        'classification_document_check_sum',
    ]
    fields = (
        'id',
        'description',
        'schedule_document',
        'schedule_document_status',
        'schedule_document_created_at',
        'schedule_document_check_sum',
        'classification_document',
        'classification_document_status',
        'classification_document_created_at',
        'classification_document_check_sum',
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ['id']
        return self.readonly_fields


class ChapterNoteAdmin(admin.ModelAdmin):
    fields = ('chapter', 'document', 'document_created_at', 'document_check_sum')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['document_check_sum', 'document_created_at', 'chapter']
        return ['document_check_sum', 'document_created_at']


class AgreementDocumentHistoryAdmin(admin.ModelAdmin):
    readonly_fields = ('agreement', 'remote_file_name', 'forced', 'created_at')
    fields = ('agreement', 'data', 'change', 'forced', 'remote_file_name', 'created_at')
    list_display = ['agreement_country', 'created_at']

    def agreement_country(self, obj):
        return obj.agreement.slug


class ChapterDocumentHistoryAdmin(admin.ModelAdmin):
    readonly_fields = ('chapter', 'document_type', 'remote_file_name', 'forced', 'created_at')
    fields = ('chapter', 'document_type', 'data', 'change', 'forced', 'remote_file_name', 'created_at')
    list_display = ['chapter', 'document_type', 'created_at']


class MFNDocumentHistoryAdmin(admin.ModelAdmin):
    readonly_fields = ('mfn_document', 'document_type', 'remote_file_name', 'forced', 'created_at')
    fields = ('mfn_document', 'document_type', 'data', 'change', 'forced', 'remote_file_name', 'created_at')
    list_display = ['document_type', 'created_at']


class MFNDocumentAdmin(admin.ModelAdmin):
    fields = (
        'document_type',
        'document',
        'document_status',
        'document_check_sum',
        'document_created_at',
        'last_checked'
    )
    readonly_fields = (
        'document_created_at',
        'document_check_sum',
        'document_type',
        'last_checked'
    )


admin.site.register(Agreement)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(ChapterNote, ChapterNoteAdmin)
admin.site.register(ChapterDocumentHistory, ChapterDocumentHistoryAdmin)
admin.site.register(AgreementDocumentHistory, AgreementDocumentHistoryAdmin)
admin.site.register(ExtendedQuota)
admin.site.register(SpecialNote)
admin.site.register(MFNDocumentHistory, MFNDocumentHistoryAdmin)
admin.site.register(LatinTerm)
admin.site.register(MFNDocument, MFNDocumentAdmin)
