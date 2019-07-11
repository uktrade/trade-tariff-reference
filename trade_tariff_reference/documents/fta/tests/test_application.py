import pytest

from unittest import mock


from trade_tariff_reference.documents.fta.application import Application
from trade_tariff_reference.tariff.tests.factories import MeursingComponentsFactory
from trade_tariff_reference.tariff.models import MeursingComponents
from documents.fta.mfn_duty import MfnDuty


pytestmark = pytest.mark.django_db


@pytest.fixture
def create_meursing_components():
    MeursingComponentsFactory(duty_amount=5, geographical_area_id='1011', reduction_indicator=3)
    MeursingComponentsFactory(duty_amount=15, geographical_area_id='1011', reduction_indicator=3)
    MeursingComponentsFactory(duty_amount=10, geographical_area_id='2000', reduction_indicator=2)
    MeursingComponentsFactory(duty_amount=30, geographical_area_id='2000', reduction_indicator=2)
    MeursingComponentsFactory(duty_amount=20, geographical_area_id='2000', reduction_indicator=1)


def get_application(country_profile):
    with mock.patch('trade_tariff_reference.documents.fta.application.Application._get_config') as mock_get_config:
        mock_get_config.return_value = None
        return Application(country_profile)


@pytest.mark.xfail
def test_get_section_chapters():
    application = get_application('israel')
    application.get_sections_chapters()
    # MPP: TODO if required add Sections and ChaptersSections models and link to GoodsNomenclature
    assert application.section_chapter_list == []


def test_get_meursing_components(create_meursing_components):
    assert MeursingComponents.objects.count() == 5
    application = get_application('israel')
    application.get_meursing_components()
    assert application.erga_omnes_average == float(10)


def test_get_meursing_percentage(create_meursing_components):
    application = get_application('israel')
    application.get_meursing_components()
    actual_percentage = application.get_meursing_percentage(2, '2000')
    assert actual_percentage == 200


def test_get_meursing_percentage_when_erga_omnes_average_none():
    application = get_application('israel')
    actual_percentage = application.get_meursing_percentage(2, '2000')
    assert actual_percentage == 100


def test_get_meursing_percentage_when_reduced_average_is_none(create_meursing_components):
    application = get_application('israel')
    actual_percentage = application.get_meursing_percentage(0, '2000')
    assert actual_percentage == 100


@pytest.mark.parametrize(
    'mfn_list,expected_rate',
    (
        (
            [],
            0
        ),
        (
            [MfnDuty(None, 1, None, None)],
            0
        ),
        (
            [
                MfnDuty('1234567800', 100, '2019-02-01', None),
                MfnDuty('1234567800', 200, '2019-01-01', None),
                MfnDuty('1234560000', 300, '2019-01-01', None),
                MfnDuty('1234567890', 150, '2019-01-01', None),
            ],
            150
        ),
        (
            [
                MfnDuty('1234567800', 100, '2019-02-01', None),
                MfnDuty('1234567800', 200, '2019-01-01', None),
                MfnDuty('1234560000', 300, '2019-01-01', None),
            ],
            200
        ),
        (
            [
                MfnDuty('1234567800', 100, '2019-02-01', None),
                MfnDuty('1234560000', 300, '2019-01-01', None),
            ],
            300
        ),

    ),
)
def test_get_mfn_rate(mfn_list, expected_rate):
    application = get_application('israel')
    application.mfn_list = mfn_list
    actual_rate = application.get_mfn_rate('1234567890', '2019-01-01')
    assert actual_rate == expected_rate
