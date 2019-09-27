from datetime import datetime, timedelta
from unittest import mock

from freezegun import freeze_time

import pytest

from trade_tariff_reference.core.tests.utils import assert_xml
from trade_tariff_reference.documents.mfn.commodity import (
    AUTHORISED_USE_NOTE,
    Commodity,
)
from trade_tariff_reference.documents.mfn.duty import Duty
from trade_tariff_reference.schedule.models import LatinTerm
from trade_tariff_reference.schedule.tests.factories import (
    LatinTermFactory,
    SeasonalQuotaFactory,
    SeasonalQuotaSeasonFactory,
    SpecialNoteFactory,
)

pytestmark = pytest.mark.django_db


EXP_FORMAT_DESCRIPTION_1 = '<w:pPr><w:jc w:val="left"/></w:pPr><w:t>-</w:t><w:tab/><w:pPr><w:jc w:val="left"/>' \
                           '</w:pPr>' \
                           '<w:t>-</w:t><w:tab/>' \
                           '<w:pPr><w:jc w:val="left"/></w:pPr><w:t>-</w:t><w:tab/>' \
                           '<w:pPr><w:jc w:val="left"/></w:pPr><w:t>-</w:t><w:tab/>' \
                           '<w:r/><w:r><w:t>Other</w:t>' \
                           '</w:r>' \
                           '<w:r/>'

EXP_FORMAT_DESCRIPTION_2 = '<w:pPr><w:jc w:val="left"/>' \
                           '</w:pPr><w:t>-</w:t><w:tab/>' \
                           '<w:r/>' \
                           '<w:r><w:t>kg liters</w:t></w:r>' \
                           '<w:r/>'


EXP_FORMAT_DESCRIPTION_3 = '<w:pPr><w:jc w:val="left"/>' \
                           '</w:pPr><w:t>-</w:t><w:tab/>' \
                           '<w:r/>' \
                           '<w:r><w:t>Other - Sweets</w:t></w:r>' \
                           '<w:r/>'

EXP_FORMAT_DESCRIPTION_4 = '<w:pPr><w:jc w:val="left"/>' \
                           '</w:pPr><w:t>-</w:t><w:tab/>' \
                           '<w:pPr>' \
                           '<w:jc w:val="left"/>' \
                           '</w:pPr><w:t>-</w:t><w:tab/>' \
                           '<w:r/>' \
                           '<w:r><w:t>Electroplated interior or exterior decorative parts consisting of:</w:t></w:r>' \
                           '<w:r><w:br/></w:r>' \
                           '<w:r><w:t xml:space="preserve"></w:t></w:r>' \
                           '<w:r><w:t>- a copolymer of acrylonitrile-butadiene-styrene (ABS), ' \
                           'whether or not mixed with polycarbonate,</w:t></w:r>' \
                           '<w:r><w:br/></w:r>' \
                           '<w:r><w:t xml:space="preserve"></w:t></w:r>' \
                           '<w:r><w:t>- layers of copper, nickel and chromium</w:t></w:r>' \
                           '<w:r><w:br/><w:t>for use in the manufacturing of parts for motor vehicles of heading ' \
                           '8701 to 8705</w:t></w:r>' \
                           '<w:r/>'

EXP_FORMAT_DESCRIPTION_5 = '<w:pPr><w:jc w:val="left"/>' \
                           '</w:pPr><w:t>-</w:t><w:tab/>' \
                           '<w:pPr>' \
                           '<w:jc w:val="left"/>' \
                           '</w:pPr><w:t>-</w:t><w:tab/>' \
                           '<w:pPr><w:jc w:val="left"/></w:pPr>' \
                           '<w:t>-</w:t><w:tab/>' \
                           '<w:pPr><w:jc w:val="left"/></w:pPr>' \
                           '<w:t>-</w:t><w:tab/>' \
                           '<w:r/>' \
                           '<w:r><w:t>Heat-, infra- and UV insulating poly(vinyl butyral) film:</w:t></w:r>' \
                           '<w:r><w:br/></w:r>' \
                           '<w:r><w:t xml:space="preserve"></w:t></w:r>' \
                           '<w:r><w:t>- laminated with a metal layer with a thickness of 0,05 mm(±0,01 mm),' \
                           '</w:t></w:r>' \
                           '<w:r><w:br/></w:r>' \
                           '<w:r><w:t xml:space="preserve"></w:t></w:r>' \
                           '<w:r><w:t>- containing by weight 29,75 % or more but not more than 40,25 % of' \
                           ' triethyleneglycol di (2-ethyl hexanoate) as plasticizer,</w:t></w:r>' \
                           '<w:r><w:br/></w:r>' \
                           '<w:r><w:t xml:space="preserve"></w:t></w:r>' \
                           '<w:r><w:t>- with a light transmission of 70 % or more' \
                           ' (as determined by the ISO 9050 standard);</w:t></w:r>' \
                           '<w:r><w:br/></w:r>' \
                           '<w:r><w:t xml:space="preserve"></w:t></w:r>' \
                           '<w:r><w:t>- with an UV transmission of 1 % or less (as determined ' \
                           'by the ISO 9050 standard);</w:t></w:r>' \
                           '<w:r><w:br/></w:r>' \
                           '<w:r><w:t xml:space="preserve"></w:t></w:r>' \
                           '<w:r><w:t>- with a total thickness of 0,43 mm (± 0,043 mm)</w:t></w:r>' \
                           '<w:r><w:br/></w:r>' \
                           '<w:r/>'

EXP_FORMAT_DESCRIPTION_6 = '<w:pPr><w:jc w:val="left"/>' \
                           '</w:pPr><w:t>-</w:t><w:tab/>' \
                           '<w:pPr><w:jc w:val="left"/></w:pPr>' \
                           '<w:t>-</w:t><w:tab/>' \
                           '<w:pPr><w:jc w:val="left"/></w:pPr>' \
                           '<w:t>-</w:t><w:tab/>' \
                           '<w:pPr><w:jc w:val="left"/></w:pPr>' \
                           '<w:t>-</w:t><w:tab/>' \
                           '<w:pPr><w:jc w:val="left"/></w:pPr>' \
                           '<w:t>-</w:t><w:tab/>' \
                           '<w:r/>' \
                           '<w:r><w:t>Thermoplastic polyurethane foil in rolls with:</w:t></w:r>' \
                           '<w:r><w:br/></w:r>' \
                           '<w:r><w:t xml:space="preserve"></w:t></w:r>' \
                           '<w:r><w:t>- a width of more than 900 mm but not more than 1016 mm,</w:t></w:r>' \
                           '<w:r><w:br/></w:r>' \
                           '<w:r><w:t xml:space="preserve"></w:t></w:r>' \
                           '<w:r><w:t>- a matt finish,</w:t></w:r>' \
                           '<w:r><w:br/></w:r>' \
                           '<w:r><w:t xml:space="preserve"></w:t></w:r>' \
                           '<w:r><w:t>- a thickness of 0,43 mm (± 0.03 mm),</w:t></w:r>' \
                           '<w:r><w:br/></w:r>' \
                           '<w:r><w:t xml:space="preserve"></w:t></w:r>' \
                           '<w:r><w:t>- an elongation to break of 420 % or more but not more than 520 %,</w:t></w:r>' \
                           '<w:r><w:br/></w:r>' \
                           '<w:r><w:t xml:space="preserve"></w:t></w:r>' \
                           '<w:r><w:t>- a tensile strength of 55 N/mm</w:t></w:r>' \
                           '<w:r><w:rPr>  <w:vertAlign w:val="superscript"/></w:rPr>' \
                           '<w:t>2</w:t>' \
                           '</w:r>' \
                           '<w:r><w:t>$ (± 3) (as determined by the method EN ISO 527)</w:t></w:r>' \
                           '<w:r><w:br/></w:r>' \
                           '<w:r><w:t xml:space="preserve"></w:t></w:r>' \
                           '<w:r><w:t>- a hardness of 90 (± 4) (as determined by the method: Shore A [ASTM D2240]),' \
                           '</w:t></w:r>' \
                           '<w:r><w:br/></w:r>' \
                           '<w:r><w:t xml:space="preserve"></w:t></w:r>' \
                           '<w:r><w:t>- wrinkle inside (waves) of 6,35 mm,</w:t></w:r>' \
                           '<w:r><w:br/></w:r>' \
                           '<w:r><w:t xml:space="preserve"></w:t></w:r>' \
                           '<w:r><w:t>- a flatness of 0,025 mm</w:t></w:r>' \
                           '<w:r><w:br/></w:r>' \
                           '<w:r/>'


EXP_SEASONAL_XML = '<w:r><w:t>2019-02-01 to 2019-05-12</w:t></w:r><w:r><w:tab/><w:t>DUTY / 100 kg</w:t></w:r>' \
                   '<w:r><w:br/></w:r>' \
                   '<w:r><w:t>2019-03-03 to 2019-07-01</w:t></w:r><w:r><w:tab/><w:t>/ 100 kg gross</w:t></w:r>'


EXP_MIXTURE_AU_FORMULA_XML = '<w:r><w:t>Formula</w:t></w:r><w:r><w:br/><w:t>AU</w:t></w:r>'


def test_initialise():
    application = mock.MagicMock()
    commodity = Commodity(application)
    assert commodity.application == application
    assert commodity.commodity_code == ''
    assert commodity.commodity_code_formatted == ''
    assert commodity.description == ''
    assert_xml(commodity.description_formatted, "<w:r/><w:r/><w:r><w:rPr>  <w:b/></w:rPr></w:r><w:r/><w:r/>")
    assert commodity.product_line_suffix == ''
    assert commodity.indents == 0
    assert commodity.leaf == 0
    assert commodity.assigned is False
    assert commodity.combined_duty == ''
    assert commodity.notes_list == []
    assert commodity.notes_string == ''
    assert commodity.duty_list == []
    assert commodity.suppress_row is False
    assert commodity.suppress_duty is False
    assert commodity.significant_children is False
    assert commodity.measure_count == 0
    assert commodity.measure_type_count == 0
    assert commodity.special_list == []
    assert commodity.child_duty_list == []
    assert commodity.indent_string == '<w:ind w:left="0" w:hanging="0"/>'
    assert commodity.significant_digits == 10


@pytest.mark.parametrize(
    'product_line_suffix,commodity_code,expected_result',
    (
        ('80', '111111111122', '1111 11 11 11'),
        ('80', '1111111111', '1111 11 11 11'),
        ('80', '1111111100', '1111 11 11'),
        ('80', '1111111000', '1111 11 10'),
        ('80', '1111110000', '1111 11'),
        ('80', '1111100000', '1111 10'),
        ('80', '1111000000', '1111'),
        ('80', '1110000000', '1110'),
        ('80', '1100000000', '1100'),
        ('80', '1000000000', '1000'),
        ('80', '0000000000', '0000'),
        ('80', '0000000001', '0000 00 00 01'),
        ('80', '0000000011', '0000 00 00 11'),
        ('80', '0000000111', '0000 00 01 11'),
        ('80', '0000001111', '0000 00 11 11'),
        ('80', '0000011111', '0000 01 11 11'),
        ('80', '0000111111', '0000 11 11 11'),
        ('80', '0001111111', '0001 11 11 11'),
        ('80', '0011111111', '0011 11 11 11'),
        ('80', '0111111111', '0111 11 11 11'),
        ('80', '0000000010', '0000 00 00 10'),
        ('77', '111111111122', ''),
        ('44', '0000000000', ''),
    ),
)
def test_format_commodity_code(product_line_suffix, commodity_code, expected_result):
    application = mock.MagicMock()
    commodity = Commodity(application, product_line_suffix=product_line_suffix)
    assert commodity.format_commodity_code(commodity_code) == expected_result


@pytest.mark.parametrize(
    'indents,expected_result',
    (
        (0, '<w:ind w:left="0" w:hanging="0"/>'),
        (1, '<w:ind w:left="113" w:hanging="113"/>'),
        (2, '<w:ind w:left="227" w:hanging="227"/>'),
        (3, '<w:ind w:left="340" w:hanging="340"/>'),
        (4, '<w:ind w:left="454" w:hanging="454"/>'),
        (5, '<w:ind w:left="567" w:hanging="567"/>'),
        (6, '<w:ind w:left="680" w:hanging="680"/>'),
        (7, '<w:ind w:left="794" w:hanging="794"/>'),
        (8, '<w:ind w:left="907" w:hanging="907"/>'),
        (9, '<w:ind w:left="1020" w:hanging="1020"/>'),
        (10, '<w:ind w:left="1134" w:hanging="1134"/>'),
        (11, '<w:ind w:left="1247" w:hanging="1247"/>'),
        (12, '<w:ind w:left="1361" w:hanging="1361"/>'),
        (13, '<w:ind w:left="0" w:hanging="0"/>'),
    ),
)
def test_get_indent_string(indents, expected_result):
    application = mock.MagicMock()
    commodity = Commodity(application, indents=indents)
    assert commodity.get_indent_string() == expected_result


@pytest.mark.parametrize(
    'db_description,indents,expected_description',
    (
        ('Other', 4, EXP_FORMAT_DESCRIPTION_1),
        ('|kg liters', 1, EXP_FORMAT_DESCRIPTION_2),
        ('Other - Sweets', 1, EXP_FORMAT_DESCRIPTION_3),
        (
            'Electroplated interior or exterior decorative parts consisting of:<br> <br><br><br>- a copolymer of'
            ' acrylonitrile-butadiene-styrene (ABS), whether or not mixed with polycarbonate,<br> <br><br><br>- layers'
            ' of copper, nickel and chromium<br>for use in the manufacturing of parts for motor vehicles of heading'
            ' 8701 to 8705',
            2,
            EXP_FORMAT_DESCRIPTION_4,
        ),
        (
            " Heat-, infra- and UV insulating poly(vinyl butyral) film:<br> <br><br><br>- laminated with a metal layer"
            " with a thickness of 0,05 mm(±0,01 mm),<br> <br><br><br>- containing by weight 29,75 % or more but not "
            "more than 40,25 % of triethyleneglycol di (2-ethyl hexanoate) as plasticizer,<br> <br><br><br>- with a "
            "light transmission of 70 % or more (as determined by the ISO 9050 standard);<br> <br><br><br>- with an "
            "UV transmission of 1 % or less (as determined by the ISO 9050 standard);<br> <br><br><br>- with "
            "a total thickness of 0,43 mm (± 0,043 mm)<br>",
            4,
            EXP_FORMAT_DESCRIPTION_5,
        ),
        (
            "Thermoplastic polyurethane foil in rolls with:<br> <br><br><br>- a width of more than 900 mm but not"
            " more than 1016 mm,<br> <br><br><br>- a matt finish,<br> <br><br><br>- a thickness"
            " of 0,43 mm (± 0.03 mm),<br> <br><br><br>- an elongation to break of 420 % or more but not more than"
            " 520 %,<br> <br><br><br>- a tensile strength of 55 N/mm<sup>2</sup>$ (± 3) (as determined by the"
            " method EN ISO 527)<br> <br><br><br>- a hardness of 90 (± 4) (as determined by the method:"
            " Shore A [ASTM D2240]),<br> <br><br><br>- wrinkle inside (waves) of 6,35 mm,<br> "
            "<br><br><br>- a flatness of 0,025 mm<br>",
            5,
            EXP_FORMAT_DESCRIPTION_6,
        )
    )
)
def test_format_description(db_description, indents, expected_description):
    application = mock.MagicMock()
    commodity = Commodity(application, indents=indents)
    actual_description = str(commodity.format_description(db_description))
    assert_xml(actual_description, expected_description)


@pytest.mark.parametrize(
    'commodity_code,expected_result',
    (
        ('', 10),
        ('0000000000', 2),
        ('1100000000', 2),
        ('1111000000', 4),
        ('1111110000', 6),
        ('1111111100', 8),
        ('1111111111', 10),
        ('0000000011', 10),
        ('0000001111', 10),
        ('0000111111', 10),
        ('0011111111', 10),
    )
)
def test_get_significant_digits(commodity_code, expected_result):
    application = mock.MagicMock()
    commodity = Commodity(application, commodity_code=commodity_code)
    assert commodity.significant_digits == expected_result


@pytest.mark.parametrize(
    'phrase,indents,expected_result',
    (
        ('hello', 0, '<i>hello</i>'),
        ('hello', 1, '<i>hello</i>'),
    )
)
def test_style_latin(phrase, indents, expected_result):
    application = mock.MagicMock()
    commodity = Commodity(application, indents=indents)
    assert commodity.style_latin(phrase) == expected_result


def test_latinise():
    LatinTermFactory(text='weather')
    LatinTermFactory(text='sunny thynnus')
    LatinTermFactory(text='weather')
    LatinTermFactory(text='sunny')

    application = mock.MagicMock()
    application.latin_phrases = get_latin_terms()

    commodity = Commodity(application)
    assert commodity.application.latin_phrases == {'weather', 'sunny thynnus', 'sunny'}
    assert (
        commodity.latinise('sunny weather is bad, no the weather is good thynnus.') ==
        '<i>sunny</i> <i>weather</i> is bad, no the <i>weather</i> is good thynnus.'
    )


def get_latin_terms():
    return set(LatinTerm.objects.values_list('text', flat=True))


@pytest.mark.parametrize(
    'product_line_suffix,'
    'commodity_code,'
    'add_season,'
    'expected_result,'
    'expected_combined_duty,'
    'expected_notes_list,'
    'expected_special_list,'
    'expected_assigned_status',
    (
        ('HELLO', '', False, 0, '', [], [], False),
        ('80', '', False, 0, '', [], [], False),
        ('80', '1234567890', False, 1, '', ['Seasonally variable rate'], ['seasonal'], True),
        ('80', '1234567890', True, 1, EXP_SEASONAL_XML, ['Seasonally variable rate'], ['seasonal'], True),
    ),
)
@freeze_time('2019-02-01 02:00:00')
def test_check_for_seasonal(
    product_line_suffix,
    commodity_code,
    add_season,
    expected_result,
    expected_combined_duty,
    expected_notes_list,
    expected_special_list,
    expected_assigned_status,
):
    seasonal_quota = SeasonalQuotaFactory(quota_order_number_id='1234567890')
    if add_season:
        start_date = datetime.now()
        end_date_1 = start_date + timedelta(days=100)
        end_date_2 = start_date + timedelta(days=150)
        SeasonalQuotaSeasonFactory(
            seasonal_quota=seasonal_quota,
            duty='DUTY DTN',
            start_date=start_date,
            end_date=end_date_1
        )
        SeasonalQuotaSeasonFactory(
            seasonal_quota=seasonal_quota,
            duty='DTN G',
            start_date=start_date + timedelta(days=30),
            end_date=end_date_2
        )

    application = mock.MagicMock()
    commodity = Commodity(application, commodity_code=commodity_code, product_line_suffix=product_line_suffix)
    assert commodity.check_for_seasonal() == expected_result
    assert commodity.notes_list == expected_notes_list
    assert commodity.special_list == expected_special_list
    assert commodity.assigned is expected_assigned_status
    assert commodity.combined_duty == expected_combined_duty


@pytest.mark.parametrize(
    'product_line_suffix,'
    'commodity_code,'
    'authorised_use_list,'
    'special_list,'
    'expected_combined_duty,'
    'expected_notes_list,'
    'expected_special_list,'
    'expected_assigned_status',
    (
        ('HELLO', '', [], [], '', [], [], False),
        ('82', '1234567890', ['1234567890'], [], '', [], [], False),
        ('80', '1234567890', ['1234567890'], ['special'], '', [], ['special'], False),
        ('80', '1234567890', ['1234567890'], [], 'AU', [AUTHORISED_USE_NOTE], ['authoriseduse'], True),
    ),
)
def test_check_for_authorised_use(
    product_line_suffix,
    commodity_code,
    authorised_use_list,
    special_list,
    expected_combined_duty,
    expected_notes_list,
    expected_special_list,
    expected_assigned_status
):
    application = mock.MagicMock(
        authorised_use_list=authorised_use_list,
    )
    commodity = Commodity(
        application,
        commodity_code=commodity_code,
        product_line_suffix=product_line_suffix
    )
    commodity.special_list = special_list
    commodity.check_for_authorised_use()
    assert commodity.combined_duty == expected_combined_duty
    assert commodity.special_list == expected_special_list
    assert commodity.assigned is expected_assigned_status
    assert commodity.notes_list == expected_notes_list


@pytest.mark.parametrize(
    'commodity_code,'
    'application_special_list,'
    'expected_special_list,'
    'expected_assigned_status',
    (
        ('', [], [], False),
        ('1234567890', [], [], False),
        ('1234567890', ['1234567890'],  ['special'], True),

    ),
)
def test_check_for_specials(
    commodity_code,
    application_special_list,
    expected_special_list,
    expected_assigned_status,
):
    application_special_list = [
        SpecialNoteFactory(quota_order_number_id=commodity_code) for commodity_code in application_special_list
    ]

    expected_notes_list = [
        special_note.note for special_note in application_special_list
    ]

    application = mock.MagicMock(
        special_list=application_special_list,
    )
    commodity = Commodity(application, commodity_code=commodity_code)
    commodity.check_for_specials()
    assert commodity.notes_list == expected_notes_list
    assert commodity.special_list == expected_special_list
    assert commodity.assigned is expected_assigned_status
    assert commodity.combined_duty == ''


@pytest.mark.parametrize(
    'commodity_code,'
    'combined_duty,'
    'expected_combined_duty,'
    'expected_notes_list,'
    'expected_special_list,'
    'expected_assigned_status',
    (
        ('', '', '', [], [], False),
        ('0300000000', '', '', [], [], False),
        ('0900000000', '', '', [], [], False),
        ('0200000000', '', '', [], [], False),
        ('0200000000', 'HELLO', 'Formula', ['Mixture rule; non-mixture: HELLO'], ['mixture'], True),
        ('0200000000', 'AU', EXP_MIXTURE_AU_FORMULA_XML, ['Mixture rule; non-mixture'], ['mixture'], True),
        ('0200000011', 'HELLO', 'HELLO', [], [], False),
        ('1000213000', 'HELLO', 'Formula', ['Mixture rule; non-mixture: HELLO'], ['mixture'], True),
        ('1101121200', 'HELLO', 'Formula', ['Mixture rule; non-mixture: HELLO'], ['mixture'], True),
        ('0904000000', 'HELLO', 'Formula', ['Mixture rule; non-mixture: HELLO'], ['mixture'], True),
        ('0905000000', 'HELLO', 'Formula', ['Mixture rule; non-mixture: HELLO'], ['mixture'], True),
        ('0906000000', 'HELLO', 'Formula', ['Mixture rule; non-mixture: HELLO'], ['mixture'], True),
        ('0907000000', 'HELLO', 'Formula', ['Mixture rule; non-mixture: HELLO'], ['mixture'], True),
        ('0908000000', 'HELLO', 'Formula', ['Mixture rule; non-mixture: HELLO'], ['mixture'], True),
        ('0909000000', 'HELLO', 'Formula', ['Mixture rule; non-mixture: HELLO'], ['mixture'], True),
        ('0910000000', 'HELLO', 'Formula', ['Mixture rule; non-mixture: HELLO'], ['mixture'], True),
        ('0911000000', '', '', [], [], False),
        ('0910000001', '', '', [], [], False),

    ),
)
def test_check_for_mixture(
    commodity_code,
    combined_duty,
    expected_combined_duty,
    expected_notes_list,
    expected_special_list,
    expected_assigned_status,
):
    application = mock.MagicMock()
    commodity = Commodity(application, commodity_code=commodity_code)
    commodity.combined_duty = combined_duty
    commodity.check_for_mixture()

    assert commodity.special_list == expected_special_list
    assert commodity.assigned is expected_assigned_status
    assert commodity.combined_duty == expected_combined_duty
    assert commodity.notes_list == expected_notes_list


@pytest.mark.parametrize(
    'notes_list,'
    'expected_notes_string',
    (
        (
            [],
            '<w:r><w:t></w:t></w:r>',
        ),
        (
            ['Note 1'],
            '<w:r><w:t>Note 1</w:t></w:r>',
        ),
        (
            ['Note 1', 'Note 2'],
            '<w:r><w:t>Note 2</w:t></w:r><w:r><w:br/><w:t>Note 1</w:t></w:r>',
        ),
        (
            ['Note 1', 'Note 2', 'Note 3'],
            '<w:r><w:t>Note 3</w:t></w:r><w:r><w:br/><w:t>Note 2</w:t></w:r><w:r><w:br/><w:t>Note 1</w:t></w:r>',
        ),
    ),
)
def test_combine_notes(
    notes_list,
    expected_notes_string,
):
    application = mock.MagicMock()
    commodity = Commodity(application)
    commodity.notes_list = notes_list
    commodity.combine_notes()
    assert commodity.notes_string == expected_notes_string


@pytest.mark.parametrize(
    'duty_list,'
    'expected_combined_duty',
    (
        ([], ''),
        (
            [
                {
                    'measure_type_id': 1,
                    'duty_amount': 1,
                    'duty_expression_id': '27',
                    'measurement_unit_code': 'KGM',
                    'measurement_unit_qualifier_code': 'G',
                    'additional_code_id': '1'
                }
            ],
            '+ FD'
        ),
        (
            [
                {
                    'measure_type_id': 1,
                    'duty_amount': 1,
                    'duty_expression_id': '27',
                    'measurement_unit_code': 'KGM',
                    'measurement_unit_qualifier_code': 'G',
                    'additional_code_id': '1'
                },
                {
                    'measure_type_id': 1,
                    'duty_amount': 1,
                    'duty_expression_id': '21',
                    'measurement_unit_code': 'MTK',
                    'measurement_unit_qualifier_code': 'G',
                    'additional_code_id': '1'
                }
            ],
            '+ FD + SD'
        ),
        (
            [
                {
                    'measure_type_id': 1,
                    'duty_amount': 1,
                    'duty_expression_id': '27',
                    'measurement_unit_code': 'KGM',
                    'measurement_unit_qualifier_code': 'G',
                    'measure_sid': 1,
                    'additional_code_id': '1'
                },
                {
                    'measure_type_id': 2,
                    'duty_amount': 1,
                    'duty_expression_id': '27',
                    'measurement_unit_code': 'MTK',
                    'measurement_unit_qualifier_code': 'G',
                    'measure_sid': 2,
                    'additional_code_id': '1',
                }
            ],
            ''
        ),
        (
            [
                {
                    'measure_type_id': '105',
                    'duty_amount': 1,
                    'duty_expression_id': '21',
                    'measurement_unit_code': 'KGM',
                    'measurement_unit_qualifier_code': 'G',
                    'measure_sid': '105',
                    'additional_code_id': '1',
                },
                {
                    'measure_type_id': 2,
                    'duty_amount': 1,
                    'duty_expression_id': '27',
                    'measurement_unit_code': 'KGM',
                    'measurement_unit_qualifier_code': 'G',
                    'measure_sid': 2,
                    'additional_code_id': '1',
                }
            ],
            '+ SD'
        ),
        (
            [
                {
                    'measure_type_id': 1,
                    'duty_amount': 1,
                    'duty_expression_id': '21',
                    'measurement_unit_code': 'KGM',
                    'measurement_unit_qualifier_code': 'G',
                    'measure_sid': '1',
                    'additional_code_id': '1',
                },
                {
                    'measure_type_id': 1,
                    'duty_amount': 1,
                    'duty_expression_id': '27',
                    'measurement_unit_code': 'KGM',
                    'measurement_unit_qualifier_code': 'G',
                    'measure_sid': 1,
                    'additional_code_id': '2',
                }
            ],
            ''
        ),
        (
            [
                {
                    'measure_type_id': 1,
                    'duty_amount': 1,
                    'duty_expression_id': '21',
                    'measurement_unit_code': 'KGM',
                    'measurement_unit_qualifier_code': 'G',
                    'measure_sid': '1',
                    'additional_code_id': '1',
                },
                {
                    'measure_type_id': 1,
                    'duty_amount': 1,
                    'duty_expression_id': '27',
                    'measurement_unit_code': 'KGM',
                    'measurement_unit_qualifier_code': 'G',
                    'measure_sid': 1,
                    'additional_code_id': '500',
                }
            ],
            '+ FD'
        ),
        (
            [
                {
                    'measure_type_id': 1,
                    'duty_amount': 1,
                    'duty_expression_id': '21',
                    'measurement_unit_code': 'KGM',
                    'measurement_unit_qualifier_code': 'G',
                    'measure_sid': '1',
                    'additional_code_id': '500',
                },
                {
                    'measure_type_id': 1,
                    'duty_amount': 1,
                    'duty_expression_id': '27',
                    'measurement_unit_code': 'KGM',
                    'measurement_unit_qualifier_code': 'G',
                    'measure_sid': 1,
                    'additional_code_id': '550',
                }
            ],
            '+ SD + FD'
        )
    )
)
def test_combine_duties(
    duty_list,
    expected_combined_duty,
):
    application = mock.MagicMock()
    commodity = Commodity(application)
    duty_list = [Duty(**duty_dict) for duty_dict in duty_list]
    commodity.duty_list = duty_list
    commodity.combine_duties()
    assert commodity.combined_duty == expected_combined_duty
