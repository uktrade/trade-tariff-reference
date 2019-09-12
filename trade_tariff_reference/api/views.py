from rest_framework.viewsets import ReadOnlyModelViewSet

from trade_tariff_reference.schedule.models import Agreement, MFNDocument

from .serializers import AgreementSerializer, MFNDocumentSerializer


class AgreementViewSet(ReadOnlyModelViewSet):
    lookup_field = 'slug'
    queryset = Agreement.objects.all()
    serializer_class = AgreementSerializer


class MFNDocumentViewSet(ReadOnlyModelViewSet):
    lookup_field = 'document_type'
    queryset = MFNDocument.objects.all()
    serializer_class = MFNDocumentSerializer
