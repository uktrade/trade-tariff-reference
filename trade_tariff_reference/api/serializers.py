from rest_framework import serializers
from rest_framework.reverse import reverse

from trade_tariff_reference.schedule.models import Agreement


class AgreementSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = Agreement
        exclude = ['id', 'document']

    def get_download_url(self, instance):
        if instance.is_document_available:
            return reverse(
                'schedule:fta:download', kwargs={'slug': instance.slug}, request=self.context.get('request'),
            )
        return ''
