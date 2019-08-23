from rest_framework.viewsets import ReadOnlyModelViewSet

from trade_tariff_reference.schedule.models import Agreement

from .serializers import AgreementSerializer


class AgreementViewSet(ReadOnlyModelViewSet):
    lookup_field = 'slug'
    queryset = Agreement.objects.all()
    serializer_class = AgreementSerializer
