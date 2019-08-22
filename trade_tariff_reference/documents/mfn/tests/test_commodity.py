from unittest import mock

import pytest

from trade_tariff_reference.documents.mfn.commodity import Commodity


def test_initialise():
    application = mock.MagicMock()
    commodity = Commodity(application)
    assert commodity.application == application
    assert commodity.commodity_code == ''
    assert commodity.commodity_code_formatted == ''
    assert commodity.description == ''
    assert commodity.description_formatted == "<w:rPr><w:b/></w:rPr><w:t xml:space='preserve'></w:t>"
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
