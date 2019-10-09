import zipfile
from datetime import datetime, timezone
from unittest import mock

from botocore.exceptions import EndpointConnectionError

from freezegun import freeze_time

from override_storage import override_storage

import pytest

from trade_tariff_reference.documents.fta.application import Application
from trade_tariff_reference.documents.fta.commodity import Commodity
from trade_tariff_reference.documents.fta.document import Document
from trade_tariff_reference.documents.fta.quota_commodity import QuotaCommodity
from trade_tariff_reference.documents.fta.quota_order_number import QuotaOrderNumber
from trade_tariff_reference.documents.fta.tests.test_application import get_mfn_siv_product
from trade_tariff_reference.documents.fta.tests.test_duty import get_duty_object
from trade_tariff_reference.documents.fta.tests.test_measure import get_measure
from trade_tariff_reference.documents.fta.tests.test_quota_balance import get_quota_balance
from trade_tariff_reference.schedule.models import AgreementDocumentHistory, ExtendedQuota
from trade_tariff_reference.schedule.tests.factories import AgreementFactory, ExtendedQuotaFactory
from trade_tariff_reference.tariff.tests.factories import (
    CurrentMeasureFactory,
    GoodsNomenclatureFactory,
    QuotaDefinitionFactory,
    QuotaOrderNumberFactory,
    QuotaOrderNumberOriginFactory,
    SimpleCurrentMeasureFactory,
)


pytestmark = pytest.mark.django_db


def test_document_initialise():
    application = mock.MagicMock(country_name='spain')
    document = Document(application)
    document.application.get_mfns_for_siv_products.assert_called_with()
    assert document.footnote_list == []
    assert document.balance_dict == {}
    assert document.duty_list == []
    assert document.supplementary_unit_list == []
    assert document.seasonal_records == 0
    assert document.wide_duty is False


def test_check_for_quotas_is_false():
    CurrentMeasureFactory(measure_type_id='140', geographical_area_id='1234', ordernumber=1)
    CurrentMeasureFactory(measure_type_id='143', geographical_area_id='1235', ordernumber=2)
    AgreementFactory(country_name='Espana', slug='spain', country_codes=['1234'])
    application = Application(country_profile='spain')
    document = Document(application)
    assert document.check_for_quotas() is False


def test_check_for_quotas_is_true():
    CurrentMeasureFactory(measure_type_id='143', geographical_area_id='1234', ordernumber=1)
    AgreementFactory(country_name='Espana', slug='spain', country_codes=['1234'])
    application = Application(country_profile='spain')
    document = Document(application)
    assert document.check_for_quotas() is True


@pytest.mark.parametrize(
    'instrument_type,expected_result',
    (
        ('hello', "'143', '146'"),
        ('preferences', "'142', '145'"),
    )
)
def test_get_measure_type_list_for_instrument_type(instrument_type, expected_result):
    application = mock.MagicMock(country_name='spain')
    document = Document(application)
    actual_result = document.get_measure_type_list_for_instrument_type(instrument_type)
    assert actual_result == expected_result


def test_get_measure_conditions():
    duty_amount = 200
    measure = get_mfn_siv_product(1, duty_amount=duty_amount)
    AgreementFactory(country_name='Espana', slug='spain', country_codes=['1011'])
    application = Application(country_profile='spain')
    document = Document(application)
    actual_result = document.get_measure_conditions("'103'")
    assert len(actual_result) == 1

    assert measure.measure_sid in actual_result
    actual_measure_condition = actual_result[measure.measure_sid]
    assert actual_measure_condition.condition_duty_amount == duty_amount
    assert actual_measure_condition.measure_sid == measure.measure_sid
    assert actual_measure_condition.measure_condition_sid == 0
    assert actual_measure_condition.component_sequence_number == 1
    assert actual_measure_condition.condition_code == 'V'


def test_get_measure_list():
    measure = get_mfn_siv_product(1, geographical_area_id='1011', measure_type_id='143')
    current_measure = CurrentMeasureFactory(
        measure_sid=measure.measure_sid,
        geographical_area_id=measure.geographical_area_id,
        measure_type_id=measure.measure_type_id,
        validity_start_date=measure.validity_start_date,
        validity_end_date=measure.validity_end_date,
        ordernumber=measure.quota_order_number_id,
        goods_nomenclature_item_id=measure.goods_nomenclature_item_id,
        reduction_indicator=measure.reduction_indicator,
    )
    AgreementFactory(country_name='Espana', slug='spain', country_codes=['1011'])
    application = Application(country_profile='spain')
    document = Document(application)
    actual_measure_list = document.get_measure_list()
    assert len(actual_measure_list) == 1
    actual_measure = actual_measure_list[0]
    assert actual_measure.commodity_code == str(current_measure.goods_nomenclature_item_id)
    assert actual_measure.measure_sid == current_measure.measure_sid
    assert actual_measure.quota_order_number_id == str(current_measure.ordernumber)
    assert actual_measure.validity_start_date == current_measure.validity_start_date
    assert actual_measure.validity_end_date == current_measure.validity_end_date
    assert actual_measure.geographical_area_id == current_measure.geographical_area_id
    assert actual_measure.reduction_indicator == current_measure.reduction_indicator


def test_get_quota_measures():
    measure = get_mfn_siv_product(1, geographical_area_id='1011', measure_type_id='143')
    current_measure = CurrentMeasureFactory(
        measure_sid=measure.measure_sid,
        geographical_area_id=measure.geographical_area_id,
        measure_type_id=measure.measure_type_id,
        validity_start_date=measure.validity_start_date,
        validity_end_date=measure.validity_end_date,
        ordernumber=measure.quota_order_number_id,
        goods_nomenclature_item_id=measure.goods_nomenclature_item_id,
        reduction_indicator=measure.reduction_indicator,
    )
    AgreementFactory(country_name='Espana', slug='spain', country_codes=['1011'])
    application = Application(country_profile='spain')
    document = Document(application)
    document.get_quota_measures()
    actual_measure_list = document.measure_list
    assert len(actual_measure_list) == 1, 'Not the correct things to assert'
    actual_measure = actual_measure_list[0]
    assert actual_measure.commodity_code == str(current_measure.goods_nomenclature_item_id)
    assert actual_measure.measure_sid == current_measure.measure_sid
    assert actual_measure.quota_order_number_id == str(current_measure.ordernumber)
    assert actual_measure.validity_start_date == current_measure.validity_start_date
    assert actual_measure.validity_end_date == current_measure.validity_end_date
    assert actual_measure.geographical_area_id == current_measure.geographical_area_id
    assert actual_measure.reduction_indicator == current_measure.reduction_indicator


def test__get_duties():
    measure = get_mfn_siv_product(1, geographical_area_id='1011', measure_type_id='143')
    current_measure = CurrentMeasureFactory(
        measure_sid=measure.measure_sid,
        geographical_area_id=measure.geographical_area_id,
        measure_type_id=measure.measure_type_id,
        validity_start_date=measure.validity_start_date,
        validity_end_date=measure.validity_end_date,
        ordernumber=measure.quota_order_number_id,
        goods_nomenclature_item_id=measure.goods_nomenclature_item_id,
        reduction_indicator=measure.reduction_indicator,
    )
    AgreementFactory(country_name='Espana', slug='spain', country_codes=['1011'])
    application = Application(country_profile='spain')

    GoodsNomenclatureFactory(goods_nomenclature_item_id=current_measure.goods_nomenclature_item_id)
    document = Document(application)
    actual_duties = list(document._get_duties("'143', '146'"))
    assert len(actual_duties) == 1
    actual_duty = actual_duties[0]

    expected_duty = {
        'additional_code_id': None,
        'additional_code_type_id': None,
        'duty_amount': None,
        'duty_expression_id': None,
        'geographical_area_id': '1011',
        'goods_nomenclature_item_id': '1',
        'measure_sid': current_measure.measure_sid,
        'measure_type_id': '143',
        'measurement_unit_code': None,
        'measurement_unit_qualifier_code': None,
        'monetary_unit_code': None,
        'ordernumber': '10',
        'reduction_indicator': 5,
        'validity_end_date': datetime(2019, 4, 2, 1, 0, tzinfo=timezone.utc),
        'validity_start_date': datetime(2019, 5, 1, 1, 0, tzinfo=timezone.utc)
    }
    assert actual_duty == expected_duty


@pytest.mark.parametrize(
    'has_quotas,called_add_first_come_first_serve,called_add_licensed',
    (
        (False, False, False),
        (True, True, True),
    )
)
@mock.patch('trade_tariff_reference.documents.fta.document.Document.add_licensed_quotas')
@mock.patch('trade_tariff_reference.documents.fta.document.Document.add_first_come_first_serve_quotas')
def test_get_quota_balances(
    mock_first_come_first_serve,
    mock_licensed,
    has_quotas,
    called_add_first_come_first_serve,
    called_add_licensed,
):
    mock_first_come_first_serve.return_value = None
    mock_licensed.return_value = None
    application = mock.MagicMock(country_name='spain')
    document = Document(application)
    document.has_quotas = has_quotas
    document.get_quota_balances()
    assert mock_licensed.called is called_add_licensed
    assert mock_first_come_first_serve.called is called_add_first_come_first_serve


def test_add_licensed_quotas():
    agreement = AgreementFactory(country_name='Espana', slug='spain', country_codes=['1011'])
    application = Application(country_profile='spain')
    licensed_quota = ExtendedQuotaFactory(
        quota_type=ExtendedQuota.LICENSED,
        agreement=application.agreement,
    )
    document = Document(application)
    document.add_licensed_quotas()
    assert licensed_quota.quota_order_number_id in document.balance_dict
    quota_balance = document.balance_dict[licensed_quota.quota_order_number_id]
    assert quota_balance.y1_balance == 0
    assert quota_balance.yx_balance == licensed_quota.opening_balance
    assert quota_balance.country == agreement.slug
    assert quota_balance.method == dict(ExtendedQuota.QUOTA_CHOICES)[ExtendedQuota.LICENSED]
    assert quota_balance.quota_order_number_id == licensed_quota.quota_order_number_id
    assert quota_balance.origin_quota == 'Yes'
    assert quota_balance.scope == licensed_quota.scope
    assert quota_balance.addendum == licensed_quota.addendum
    assert quota_balance.measurement_unit_code == 'KGM'
    assert quota_balance.validity_start_date_2019 == datetime(2018, 1, 1, 0, 0)
    assert quota_balance.validity_end_date_2019 == datetime(2019, 12, 31, 0, 0)


@pytest.mark.parametrize(
    'has_extended_info,expected_origin_quota,expected_scope,expected_addendum,expected_measurement_unit_code',
    (
        (False, '', '', '', 'FS'),
        (True, 'Yes', 'FCFS Scope', 'FCFS Addendum', 'FS'),
    )
)
def test_add_first_come_serve_quotas(
    has_extended_info,
    expected_origin_quota,
    expected_addendum,
    expected_scope,
    expected_measurement_unit_code,
):
    geographical_area_id = '1011'
    country_profile = 'spain'
    quota_order_number = QuotaOrderNumberFactory()

    quota_definition = QuotaDefinitionFactory(
        quota_order_number=quota_order_number,
        initial_volume=2000,
        volume=3000,
        measurement_unit_code='FS'
    )
    QuotaOrderNumberOriginFactory(
        quota_order_number_sid=quota_order_number.quota_order_number_sid,
        geographical_area_id=geographical_area_id,
    )
    agreement = AgreementFactory(
        country_name=country_profile.capitalize(),
        slug=country_profile,
        country_codes=[geographical_area_id]
    )
    if has_extended_info:
        ExtendedQuotaFactory(
            quota_type=ExtendedQuota.FIRST_COME_FIRST_SERVED,
            agreement=agreement,
            scope='FCFS Scope',
            addendum='FCFS Addendum',
            measurement_unit_code='KGM',
            is_origin_quota=True,
            quota_order_number_id=quota_order_number.quota_order_number_id
        )

    application = Application(
        country_profile=country_profile
    )
    document = Document(application)
    document.add_first_come_first_serve_quotas()
    assert quota_order_number.quota_order_number_id in document.balance_dict
    quota_balance = document.balance_dict[quota_order_number.quota_order_number_id]
    assert quota_balance.quota_order_number_id == quota_order_number.quota_order_number_id
    assert quota_balance.y1_balance == quota_definition.initial_volume
    assert quota_balance.yx_balance == quota_definition.volume
    assert quota_balance.country == agreement.slug
    assert quota_balance.method == dict(ExtendedQuota.QUOTA_CHOICES)[ExtendedQuota.FIRST_COME_FIRST_SERVED]
    assert quota_balance.validity_start_date_2019 == datetime(2018, 1, 1, 0, 0)
    assert quota_balance.validity_end_date_2019 == datetime(2019, 12, 31, 0, 0)

    assert quota_balance.origin_quota == expected_origin_quota
    assert quota_balance.scope == expected_scope
    assert quota_balance.addendum == expected_addendum
    assert quota_balance.measurement_unit_code == expected_measurement_unit_code


@pytest.mark.parametrize(
    'has_quotas,called_execute_sql',
    (
        (False, False),
        (True, True),
    )
)
@mock.patch('trade_tariff_reference.documents.database.DatabaseConnect.execute_sql')
def test_get_quota_definitions_when_has_quotas(
    mock_execute_sql,
    has_quotas,
    called_execute_sql,
):
    mock_execute_sql.return_value = []
    application = mock.MagicMock(country_name='spain', execute_sql=mock_execute_sql)
    document = Document(application)
    document.has_quotas = has_quotas
    document.q = []
    document.quota_order_number_list = []
    document.get_quota_definitions()
    assert mock_execute_sql.called is called_execute_sql


@pytest.mark.parametrize(
    'quota_order_number_id,add_balance,expected_quota_order_number_sid,expected_definition',
    (
        (
            '123456',
            True,
            123456,
            {
                'critical_state': None,
                'critical_threshold': None,
                'initial_volume': 6000,
                'maximum_precision': None,
                'measurement_unit_code': '',
                'measurement_unit_qualifier_code': '',
                'monetary_unit_code': '',
                'quota_definition_sid': None,
                'quota_order_number_id': '123456',
                'quota_order_number_sid': 123456,
                'validity_end_date': datetime(2020, 12, 31, 0, 0, tzinfo=timezone.utc),
                'validity_start_date': datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc),
                'volume': 3000,
            }
        ),
        (
            '123456',
            False,
            123456,
            {
                'critical_state': None,
                'critical_threshold': None,
                'initial_volume': 2000,
                'maximum_precision': None,
                'measurement_unit_code': '',
                'measurement_unit_qualifier_code': '',
                'monetary_unit_code': '',
                'quota_definition_sid': None,
                'quota_order_number_id': '123456',
                'quota_order_number_sid': 123456,
                'validity_end_date': datetime(2020, 12, 31, 0, 0, tzinfo=timezone.utc),
                'validity_start_date': datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc),
                'volume': 3000,
            }
        ),
        (
            '094346',
            True,
            0,
            {
                'critical_state': 'Y',
                'critical_threshold': 90,
                'initial_volume': 6000,
                'maximum_precision': 3,
                'measurement_unit_code': 'KGM',
                'measurement_unit_qualifier_code': '',
                'monetary_unit_code': '',
                'quota_definition_sid': 0,
                'quota_order_number_id': '094346',
                'quota_order_number_sid': 0,
                'validity_end_date': datetime(2011, 1, 19, 0, 0),
                'validity_start_date': datetime(2010, 1, 20, 0, 0),
                'volume': 6000,
            }
        ),
    ),
)
def test_get_quota_definitions(
    quota_order_number_id,
    add_balance,
    expected_quota_order_number_sid,
    expected_definition
):
    geographical_area_id = '1011'
    country_profile = 'spain'

    quota_order_number = QuotaOrderNumberFactory(
        id=quota_order_number_id,
        quota_order_number_sid=str(quota_order_number_id)
    )
    if not quota_order_number_id.startswith('094'):
        QuotaDefinitionFactory(
            quota_order_number_id=quota_order_number.id,
            quota_order_number_sid=quota_order_number.quota_order_number_sid,
            initial_volume=2000,
            volume=3000,
            measurement_unit_code=''
        )

    AgreementFactory(
        country_name=country_profile.capitalize(),
        slug=country_profile,
        country_codes=[geographical_area_id]
    )
    application = Application(
        country_profile=country_profile
    )

    document = Document(application)
    document.has_quotas = True

    if add_balance:
        qb = get_quota_balance(
            quota_order_number_id=quota_order_number.quota_order_number_id,
            y1_balance=6000,
        )
        document.balance_dict[quota_order_number.quota_order_number_id] = qb

    document.q = [quota_order_number.quota_order_number_id]
    qon = QuotaOrderNumber(quota_order_number.quota_order_number_id)
    assert document.quota_definition_list == []
    document.quota_order_number_list = [qon]
    document.get_quota_definitions()
    assert len(qon.quota_definition_list) == 1
    assert qon.quota_definition_list[0].quota_order_number_id == str(quota_order_number_id)
    assert len(document.quota_definition_list) == 1
    assert_object(document.quota_definition_list[0], expected_definition)


def assert_object(actual_definition, expected_definition):
    for key, expected_value in expected_definition.items():
        assert getattr(actual_definition, key) == expected_value, f'{key}'


@pytest.mark.parametrize(
    'context,expected_template',
    (
        ({}, 'xml/fta/document_noquotas.xml'),
        ({'HAS_QUOTAS': True}, 'xml/fta/document_hasquotas.xml'),
    ),
)
@mock.patch('trade_tariff_reference.documents.fta.document.render_to_string')
def test_get_document_xml(mock_render_to_string, context, expected_template):
    mock_render_to_string.return_value = 'XML'
    application = mock.MagicMock(country_name='spain')
    document = Document(application)
    actual_result = document.get_document_xml(context)
    assert actual_result == 'XML'
    assert mock_render_to_string.call_count == 1
    mock_render_to_string.assert_called_with(expected_template, context)


@pytest.mark.parametrize(
    'suppress,expected_result',
    (
        (
            None,
            {
                'TARIFF_TABLE_ROWS': [],
                'TARIFF_WIDTH_CLASSIFICATION': '400',
                'TARIFF_WIDTH_DUTY': '1450'
            },
        ),
        (
            True,
            {
                'TARIFF_TABLE_ROWS': [],
                'TARIFF_WIDTH_CLASSIFICATION': '400',
                'TARIFF_WIDTH_DUTY': '1450'
            },
        ),
        (
            False,
            {
                'TARIFF_TABLE_ROWS': [{'COMMODITY': '1245 67 89 0', 'DUTY': 'Test duty string'}],
                'TARIFF_WIDTH_CLASSIFICATION': '400',
                'TARIFF_WIDTH_DUTY': '1450'
            },
        ),
    )
)
def test_print_tariffs(suppress, expected_result):
    application = mock.MagicMock(country_name='spain')
    document = Document(application)
    if suppress is None:
        document.commodity_list = []
    else:
        commodity = QuotaCommodity('124567890', None)
        commodity.suppress = suppress
        commodity.duty_string = 'Test duty string<w:r><w:br/></w:r>'
        document.commodity_list = [commodity]
    actual_result = document.print_tariffs()
    assert actual_result == expected_result


@pytest.mark.parametrize(
    'context,force,expected_template,expected_document_xml,expected_change,raise_write_exception',
    (
        (
            {'fake': 'context'},
            True,
            'xml/fta/document_noquotas.xml',
            'XML',
            {'dictionary_item_added': ["root['fake']"]},
            False,
        ),
        (
            {},
            False,
            'xml/fta/document_noquotas.xml',
            None,
            {},
            False,
        ),
        (
            {'fake': 'context'},
            True,
            'xml/fta/document_noquotas.xml',
            'XML',
            {},
            True,
        ),
    ),
)
@mock.patch('trade_tariff_reference.documents.fta.document.Document.write')
@mock.patch('trade_tariff_reference.documents.fta.document.render_to_string')
def test_create_document(
    mock_render_to_string,
    mock_write,
    context,
    force,
    expected_template,
    expected_document_xml,
    expected_change,
    raise_write_exception,
):
    fake_file_name = 'fake_file.txt'

    mock_write.return_value = fake_file_name
    if raise_write_exception:
        mock_write.side_effect = EndpointConnectionError(endpoint_url='')

    mock_render_to_string.return_value = expected_document_xml
    agreement = AgreementFactory(country_name='Espana', slug='spain', country_codes=['1011'])
    application = Application(country_profile='spain', force_document_generation=force)
    document = Document(application)
    document.create_document(context)

    if expected_document_xml:
        mock_render_to_string.assert_called_with(expected_template, context)
        mock_write.asssert_called_with(expected_document_xml)
    else:
        assert mock_render_to_string.called is False
        assert mock_write.called is False

    if expected_change:
        document_history = AgreementDocumentHistory.objects.get(
            agreement=agreement
        )
        assert document_history.forced is force
        assert document_history.data == context
        assert document_history.change == expected_change
        assert document_history.remote_file_name == fake_file_name
    else:
        assert AgreementDocumentHistory.objects.filter(
            agreement=agreement
        ).exists() is False


@pytest.mark.parametrize(
    'quota_order_numbers,has_quotas,expected_q',
    (
        (
            [],
            False,
            [],
        ),
        (
            ['123456'],
            True,
            ['123456'],
        ),
        (
            ['123456', '654321'],
            True,
            ['123456', '654321'],
        ),
    ),
)
def test_get_quota_order_numbers(quota_order_numbers, has_quotas, expected_q):
    AgreementFactory(country_name='Espana', slug='spain', country_codes=['1011'])
    application = Application(country_profile='spain')
    ignored_measure = get_mfn_siv_product(
        1,
        geographical_area_id='1011',
        measure_type_id='142',
        measure_quota_number='99999'
    )
    CurrentMeasureFactory(
        measure_sid=ignored_measure.measure_sid,
        geographical_area_id=ignored_measure.geographical_area_id,
        measure_type_id=ignored_measure.measure_type_id,
        validity_start_date=ignored_measure.validity_start_date,
        validity_end_date=ignored_measure.validity_end_date,
        ordernumber=ignored_measure.quota_order_number_id,
        goods_nomenclature_item_id=ignored_measure.goods_nomenclature_item_id,
        reduction_indicator=ignored_measure.reduction_indicator,
    )

    for quota_order_number in quota_order_numbers:
        measure = get_mfn_siv_product(
            1,
            geographical_area_id='1011',
            measure_type_id='143',
            measure_quota_number=quota_order_number
        )
        CurrentMeasureFactory(
            measure_sid=measure.measure_sid,
            geographical_area_id=measure.geographical_area_id,
            measure_type_id=measure.measure_type_id,
            validity_start_date=measure.validity_start_date,
            validity_end_date=measure.validity_end_date,
            ordernumber=measure.quota_order_number_id,
            goods_nomenclature_item_id=measure.goods_nomenclature_item_id,
            reduction_indicator=measure.reduction_indicator,
        )
    document = Document(application)
    document.get_quota_order_numbers()
    assert document.has_quotas is has_quotas
    assert document.q == expected_q
    assert len(document.quota_order_number_list) == len(expected_q)
    for qon in document.quota_order_number_list:
        assert qon.quota_order_number_id in expected_q


@pytest.mark.parametrize(
    'measures,expected_local_sivs_commodities_only',
    (
        (
            [],
            [],
        ),
        (
            [
                {'goods_nomenclature_item_id': 1, 'duty_amount': 0},
                {'goods_nomenclature_item_id': 2, 'condition_code': 'G'}
            ],
            [],
        ),
        (
            [
                {'goods_nomenclature_item_id': 1, 'duty_amount': 0},
                {'goods_nomenclature_item_id': 2, 'condition_code': 'G'},
                {'goods_nomenclature_item_id': 20, 'duty_amount': 200, 'start_date': '2018-01-01 01:00:00'},
            ],
            ['20'],
        ),
    ),
)
def test_get_commodities_for_local_sivs(measures, expected_local_sivs_commodities_only):
    AgreementFactory(country_name='Espana', slug='spain', country_codes=['1011'])
    application = Application(country_profile='spain')
    for measure_properties in measures:
        measure = get_mfn_siv_product(
            measure_properties.pop('goods_nomenclature_item_id'),
            geographical_area_id='1011',
            measure_type_id='142',
            measure_quota_number='99999',
            **measure_properties
        )
        CurrentMeasureFactory(
            measure_sid=measure.measure_sid,
            geographical_area_id=measure.geographical_area_id,
            measure_type_id=measure.measure_type_id,
            validity_start_date=measure.validity_start_date,
            validity_end_date=measure.validity_end_date,
            ordernumber=measure.quota_order_number_id,
            goods_nomenclature_item_id=measure.goods_nomenclature_item_id,
            reduction_indicator=measure.reduction_indicator,
        )

    document = Document(application)
    actual_local_sivs, actual_local_sivs_commodities_only = document.get_commodities_for_local_sivs()
    assert actual_local_sivs_commodities_only == expected_local_sivs_commodities_only
    assert len(actual_local_sivs) == len(expected_local_sivs_commodities_only)
    for local_siv in actual_local_sivs:
        assert local_siv.goods_nomenclature_item_id in expected_local_sivs_commodities_only


@pytest.mark.parametrize(
    'commodity_list,expected_resolve_measures_call_count',
    (
        (
            [],
            0
        ),
        (
            ['123456'],
            1
        ),
        (
            ['123456', '111111', '222222'],
            3
        ),
    ),
)
@mock.patch('trade_tariff_reference.documents.fta.commodity.Commodity.resolve_measures')
def test_resolve_measures(mock_resolve_measures, commodity_list, expected_resolve_measures_call_count):
    mock_resolve_measures.return_value = None
    application = mock.MagicMock(country_name='spain')
    document = Document(application)
    document.commodity_list = [Commodity(commodity_code) for commodity_code in commodity_list]
    document.resolve_measures()
    assert mock_resolve_measures.call_count == expected_resolve_measures_call_count


@pytest.mark.parametrize(
    'measure_list,expected_combine_duties_call_count',
    (
        (
            [],
            0
        ),
        (
            ['123456'],
            1
        ),
        (
            ['123456', '111111', '222222'],
            3
        ),
    ),
)
@mock.patch('trade_tariff_reference.documents.fta.measure.Measure.combine_duties')
def test_combine_duties(mock_combine_duties, measure_list, expected_combine_duties_call_count):
    mock_combine_duties.return_value = None
    application = mock.MagicMock(country_name='spain')
    document = Document(application)
    document.measure_list = [get_measure(measure_sid=measure_sid) for measure_sid in measure_list]
    document.combine_duties()
    assert mock_combine_duties.call_count == expected_combine_duties_call_count


@pytest.mark.parametrize(
    'commodity_list,measure_list,expected_assigned_measure',
    (
        (
            ['111111'],
            [{'measure_sid': '123456', 'commodity_code': '111111'}],
            True,
        ),
        (
            ['111111'],
            [{'measure_sid': '123456', 'commodity_code': '111112'}],
            False,
        ),
    ),
)
@mock.patch('trade_tariff_reference.documents.fta.measure.Measure.combine_duties')
def test_assign_measures_to_commodities(mock_combine_duties, commodity_list, measure_list, expected_assigned_measure):
    mock_combine_duties.return_value = None
    application = mock.MagicMock(country_name='spain')
    document = Document(application)

    commodity_list = [Commodity(commodity_code) for commodity_code in commodity_list]
    measure_list = [get_measure(**measure_properties) for measure_properties in measure_list]

    document.commodity_list = commodity_list
    document.measure_list = measure_list
    for commodity in commodity_list:
        assert commodity.measure_list == []

    document.assign_measures_to_commodities()
    for commodity in document.commodity_list:
        if expected_assigned_measure:
            assert len(commodity.measure_list) == 1
            # TODO: MPP not a very dynamic test as it makes assumptions. Consider a better way to assert
            assert commodity.measure_list[0].measure_sid == measure_list[0].measure_sid
        else:
            assert commodity.measure_list == []


@pytest.mark.parametrize(
    'duty_list,measure_list,expected_assigned_duty',
    (
        (
            [{'measure_sid': '123456'}],
            [{'measure_sid': '123456'}],
            True,
        ),
        (
            [{'measure_sid': '111111'}],
            [{'measure_sid': '123456'}],
            False,
        ),
    ),
)
@mock.patch('trade_tariff_reference.documents.fta.measure.Measure.combine_duties')
def test_assign_duties_to_measures(mock_combine_duties, duty_list, measure_list, expected_assigned_duty):
    mock_combine_duties.return_value = None
    application = mock.MagicMock(country_name='spain')
    document = Document(application)

    duty_list = [get_duty_object(**duty_properties) for duty_properties in duty_list]
    measure_list = [get_measure(**measure_properties) for measure_properties in measure_list]

    document.duty_list = duty_list
    document.measure_list = measure_list
    for measure in measure_list:
        assert measure.duty_list == []

    document.assign_duties_to_measures()
    for measure in document.measure_list:
        if expected_assigned_duty:
            assert len(measure.duty_list) == 1
            # TODO: MPP not a very dynamic test as it makes assumptions. Consider a better way to assert
            assert measure.duty_list[0].measure_sid == measure_list[0].measure_sid
        else:
            assert measure.duty_list == []


@pytest.mark.parametrize(
    'instrument_type,'
    'measure_type_id,'
    'expected_duty_list,'
    'expected_measure_list,'
    'expected_commodity_list,'
    'expected_quota_order_number_list',
    (
        (
            'preferences',
            '142',
            [
                {
                    'commodity_code': '1',
                    'additional_code_type_id': '',
                    'additional_code_id': '',
                    'measure_type_id': '142',
                    'duty_expression_id': '01',
                    'duty_amount': 100,
                    'monetary_unit_code': '',
                    'measurement_unit_code': '',
                    'measurement_unit_qualifier_code': '',
                    'quota_order_number_id': '10',
                    'geographical_area_id': '1011',
                    'validity_start_date': datetime(2019, 5, 1, 1, 0, tzinfo=timezone.utc),
                    'validity_end_date': datetime(2019, 4, 2, 1, 0, tzinfo=timezone.utc),
                    'reduction_indicator': 5,
                    'is_siv': True,
                    'local_sivs_commodities_only': ['1'],
                }
            ],
            [
                {
                    'commodity_code': '1',
                    'quota_order_number_id': '10',
                    'validity_start_date': datetime(2019, 5, 1, 1, 0, tzinfo=timezone.utc),
                    'validity_end_date': datetime(2019, 4, 2, 1, 0, tzinfo=timezone.utc),
                    'geographical_area_id': '1011',
                    'reduction_indicator': 5,
                },
            ],
            [
                {
                    'commodity_code': '1',
                }
            ],
            [
                {
                    'quota_order_number_id': '10',
                }
            ],
        ),
        (
            'quotas',
            '143',
            [
                {
                    'commodity_code': '1',
                    'additional_code_type_id': '',
                    'additional_code_id': '',
                    'measure_type_id': '143',
                    'duty_expression_id': '01',
                    'duty_amount': 100,
                    'monetary_unit_code': '',
                    'measurement_unit_code': '',
                    'measurement_unit_qualifier_code': '',
                    'quota_order_number_id': '10',
                    'geographical_area_id': '1011',
                    'validity_start_date': datetime(2019, 5, 1, 1, 0, tzinfo=timezone.utc),
                    'validity_end_date': datetime(2019, 4, 2, 1, 0, tzinfo=timezone.utc),
                    'reduction_indicator': 5,
                    'is_siv': True,
                    'local_sivs_commodities_only': ['1'],
                }
            ],
            [
                {
                    'commodity_code': '1',
                    'quota_order_number_id': '10',
                    'validity_start_date': datetime(2019, 5, 1, 1, 0, tzinfo=timezone.utc),
                    'validity_end_date': datetime(2019, 4, 2, 1, 0, tzinfo=timezone.utc),
                    'geographical_area_id': '1011',
                    'reduction_indicator': 5,
                },
            ],
            [
                {
                    'commodity_code': '1',
                }
            ],
            [
                {
                    'quota_order_number_id': '10',
                }
            ]
        ),
    )
)
def test_get_duties(
    instrument_type,
    measure_type_id,
    expected_duty_list,
    expected_measure_list,
    expected_commodity_list,
    expected_quota_order_number_list
):
    measure = get_mfn_siv_product(1, geographical_area_id='1011', measure_type_id=measure_type_id)
    current_measure = CurrentMeasureFactory(
        measure_sid=measure.measure_sid,
        geographical_area_id=measure.geographical_area_id,
        measure_type_id=measure.measure_type_id,
        validity_start_date=measure.validity_start_date,
        validity_end_date=measure.validity_end_date,
        ordernumber=measure.quota_order_number_id,
        goods_nomenclature_item_id=measure.goods_nomenclature_item_id,
        reduction_indicator=measure.reduction_indicator,
    )
    GoodsNomenclatureFactory(goods_nomenclature_item_id=current_measure.goods_nomenclature_item_id)
    AgreementFactory(country_name='Espana', slug='spain', country_codes=['1011'])
    application = Application(country_profile='spain')
    document = Document(application)
    document.get_duties(instrument_type)

    assert len(document.duty_list) == len(expected_duty_list)
    if document.duty_list:
        assert_object(document.duty_list[0], expected_duty_list[0])

    assert len(document.measure_list) == len(expected_measure_list)
    if document.measure_list:
        assert_object(document.measure_list[0], expected_measure_list[0])

    assert len(document.commodity_list) == len(expected_commodity_list)
    if document.commodity_list:
        assert_object(document.commodity_list[0], expected_commodity_list[0])

    assert len(document.quota_order_number_list) == len(expected_quota_order_number_list)
    if document.quota_order_number_list:
        assert_object(document.quota_order_number_list[0], expected_quota_order_number_list[0])


@override_storage()
def test_write():
    file_contents = 'XML'
    agreement = AgreementFactory(country_name='Espana', slug='spain', country_codes=['1011'])
    application = Application(country_profile='spain')
    document = Document(application)
    actual_remote_file_name = document.write(file_contents)
    agreement.refresh_from_db()
    assert agreement.document.name == actual_remote_file_name
    with zipfile.ZipFile(agreement.document) as fh:
        actual_files = [f.filename for f in fh.filelist]
        assert set(actual_files) == {
            '[Content_Types].xml',
            '_rels/.rels',
            'word/webSettings.xml',
            'word/footer2.xml',
            'word/settings.xml',
            'word/footnotes.xml',
            'word/footer1.xml',
            'word/fontTable.xml',
            'word/header1.xml',
            'word/document.xml',
            'word/endnotes.xml',
            'word/styles.xml',
            'word/numbering.xml',
            'word/_rels/document.xml.rels',
            'word/theme/theme1.xml',
            'customXml/item1.xml',
            'customXml/itemProps1.xml',
            'customXml/_rels/item1.xml.rels'
        }
        actual_document_xml = fh.read('word/document.xml')
        assert actual_document_xml == bytes(file_contents, 'utf-8')
