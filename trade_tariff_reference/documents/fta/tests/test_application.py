import pytest

from unittest import mock


from trade_tariff_reference.documents.fta.application import Application
from trade_tariff_reference.tariff.tests.factories import MeursingComponentsFactory
from trade_tariff_reference.tariff.models import MeursingComponents


pytestmark = pytest.mark.django_db


@pytest.fixture
def create_meursing_components():
    # Unsure why clean up is not working need to manually delete the factories
    MeursingComponents.objects.all().delete()
    MeursingComponentsFactory(duty_amount=5, geographical_area_id='1011')
    MeursingComponentsFactory(duty_amount=15, geographical_area_id='1011')
    MeursingComponentsFactory(duty_amount=10, geographical_area_id='2000')


def get_application(country_profile):
    with mock.patch('trade_tariff_reference.documents.fta.application.Application._get_config') as mock_get_config:
        mock_get_config.return_value = None
        return Application(country_profile)


def test_get_section_chapters():
    application = get_application('israel')
    application.get_sections_chapters()
    # MPP: TODO if required add Sections and ChaptersSections models and link to GoodsNomenclature
    assert application.section_chapter_list == []


@pytest.mark.django_db
def test_get_meursing_components(create_meursing_components):
    assert MeursingComponents.objects.count() == 3
    application = get_application('israel')
    application.get_meursing_components()
    assert application.erga_omnes_average == float(10)

