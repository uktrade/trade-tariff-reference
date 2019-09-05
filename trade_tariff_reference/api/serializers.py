from rest_framework import serializers
from rest_framework.reverse import reverse

from trade_tariff_reference.schedule.models import (
    Agreement,
    MFNDocument,
)


class AgreementSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = Agreement
        exclude = ['id', 'document']

    def get_download_url(self, instance):
        if instance.is_document_available:
            return reverse(
                'schedule:fta:download',
                kwargs={'slug': instance.slug},
                request=self.context.get('request'),
            )
        return ''


class MFNDocumentSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = MFNDocument
        exclude = ['id', 'document', 'document_check_sum']

    def get_download_url(self, instance):
        if instance.is_document_available:
            return reverse(
                'schedule:mfn:download',
                kwargs={'document_type': instance.document_type},
                request=self.context.get('request'),
            )
        return ''
