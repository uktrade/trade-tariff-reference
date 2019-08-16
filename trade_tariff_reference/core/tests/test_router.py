from django.test import override_settings

import pytest

from trade_tariff_reference.tariff.tests.factories import CurrentMeasureFactory


class TestRouter:

    @override_settings(MANAGE_TARIFF_DATABASE=False)
    def test_db_for_write(self):
        with pytest.raises(Exception) as exc_info:
            CurrentMeasureFactory()
        assert 'This data is readonly' in str(exc_info.value)
