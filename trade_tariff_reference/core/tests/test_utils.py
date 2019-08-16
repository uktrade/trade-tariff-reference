import os

from django.test import override_settings

import pytest

from trade_tariff_reference.core.utils import load_data_from_sql
from trade_tariff_reference.schedule.tests.factories import AgreementFactory


@pytest.mark.django_db
def test_load_sql_file():
    agreement = AgreementFactory()
    TEST_SQL_DIR = os.path.dirname(os.path.abspath(__file__))
    with override_settings(BASE_DIR=TEST_SQL_DIR):
        result = load_data_from_sql('test_utils.sql', {'slug': agreement.slug}, 'default')
        assert len(result) == 1
        assert result[0][0] == agreement.agreement_name
