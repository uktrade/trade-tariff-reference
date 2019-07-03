import pytest

from trade_tariff_reference.tariff.tests.factories import MeasureFactory

pytestmark = pytest.mark.django_db


def test_measures_model():
    measure = MeasureFactory(status='LOADED')
    assert measure.status == 'LOADED'
