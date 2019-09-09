from unittest import mock

import pytest

from trade_tariff_reference.core.tests.utils import assert_xml
from trade_tariff_reference.documents.mfn.commodity import Commodity


EXP_FORMAT_DESCRIPTION_1 = '<w:pPr><w:jc w:val="left"/></w:pPr><w:t>-</w:t><w:tab/><w:pPr><w:jc w:val="left"/>' \
                           '</w:pPr>' \
                           '<w:t>-</w:t><w:tab/>' \
                           '<w:pPr><w:jc w:val="left"/></w:pPr><w:t>-</w:t><w:tab/>' \
                           '<w:pPr><w:jc w:val="left"/></w:pPr><w:t>-</w:t><w:tab/><w:p>' \
                           '<w:r/><w:r><w:t>Other</w:t>' \
                           '</w:r>' \
                           '<w:r/>' \
                           '</w:p>'

EXP_FORMAT_DESCRIPTION_2 = '<w:pPr><w:jc w:val="left"/>' \
                           '</w:pPr><w:t>-</w:t><w:tab/>' \
                           '<w:p>' \
                           '<w:r/>' \
                           '<w:r><w:t>kg liters</w:t></w:r>' \
                           '<w:r/>' \
                           '</w:p>'


EXP_FORMAT_DESCRIPTION_3 = '<w:pPr><w:jc w:val="left"/>' \
                           '</w:pPr><w:t>-</w:t><w:tab/>' \
                           '<w:p>' \
                           '<w:r/>' \
                           '<w:r><w:t>Other - Sweets</w:t></w:r>' \
                           '<w:r/>' \
                           '</w:p>'

EXP_FORMAT_DESCRIPTION_4 = '<w:pPr><w:jc w:val="left"/>' \
                           '</w:pPr><w:t>-</w:t><w:tab/>' \
                           '<w:pPr>' \
                           '<w:jc w:val="left"/>' \
                           '</w:pPr><w:t>-</w:t><w:tab/>' \
                           '<w:p>' \
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
                           '<w:r/>' \
                           '</w:p>'

EXP_FORMAT_DESCRIPTION_5 = '<w:pPr><w:jc w:val="left"/>' \
                           '</w:pPr><w:t>-</w:t><w:tab/>' \
                           '<w:pPr>' \
                           '<w:jc w:val="left"/>' \
                           '</w:pPr><w:t>-</w:t><w:tab/>' \
                           '<w:pPr><w:jc w:val="left"/></w:pPr>' \
                           '<w:t>-</w:t><w:tab/>' \
                           '<w:pPr><w:jc w:val="left"/></w:pPr>' \
                           '<w:t>-</w:t><w:tab/>' \
                           '<w:p>' \
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
                           '<w:r/>' \
                           '</w:p>'

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
                           '<w:p><w:r/>' \
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
                           '<w:r/>' \
                           '</w:p>'


def test_initialise():
    application = mock.MagicMock()
    commodity = Commodity(application)
    assert commodity.application == application
    assert commodity.commodity_code == ''
    assert commodity.commodity_code_formatted == ''
    assert commodity.description == ''
    assert_xml(commodity.description_formatted, "<w:p><w:r/></w:p>")
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
