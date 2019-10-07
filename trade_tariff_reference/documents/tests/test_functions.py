import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from trade_tariff_reference.documents import functions


@pytest.mark.parametrize(
    'abbreviation,expected_result',
    (
        (
            'TNE', 'tonne'
        ),
        (
            'HELLO', 'HELLO'
        ),
        (
            None, None
        ),
        (
            'ASV', '% vol'
        ),
        (
            'DTN', '100 kg'
        ),
        (
            'HMT', '100 m'
        ),
        (
            'KGM', 'kg'
        ),
        (
            'MWH', '1,000 kWh'
        ),
        (
            'NCL', 'ce/el'
        ),
        (
            'LPA', 'l alc. 100%'
        ),
    ),
)
def test_get_measurement_unit(abbreviation, expected_result):
    assert functions.get_measurement_unit(abbreviation) == expected_result


@pytest.mark.parametrize(
    'abbreviation,expected_result',
    (
        (
            'A', 'tot alc',
        ),
        (
            'C', '1 000',
        ),
        (
            'E', 'net drained wt',
        ),
        (
            'G', 'gross',
        ),
        (
            'M', 'net dry',
        ),
        (
            'P', 'lactic matter',
        ),
        (
            'R', 'std qual',
        ),
        (
            'S', 'raw sugar',
        ),
        (
            'T', 'dry lactic matter',
        ),
        (
            'X', 'hl',
        ),
        (
            'Z', '% sacchar'
        ),
        (
            1, '',
        ),
        (
            None, '',
        ),
        (
            'HELLO', ''
        ),
    ),
)
def test_get_measurement_unit_qualifier_code(abbreviation, expected_result):
    assert functions.get_measurement_unit_qualifier_code(abbreviation) == expected_result


@pytest.mark.parametrize(
    'value,expected_result',
    (
        (1, '1'),
        (None, ''),
        (True, 'True'),
        ('hello', 'hello'),
        (f'{0:1}', '0')
    ),
)
def test_mstr(value, expected_result):
    assert functions.mstr(value) == expected_result


@pytest.mark.parametrize(
    'value,expected_result',
    (
        ('', ''),
        ([], ''),
        (['1'], "'1'"),
        (['1', '2'], "'1', '2'"),
        (['1', 2], "'1', '2'"),
        (['HELLO', 'GOOD', 'BYE'], "'HELLO', 'GOOD', 'BYE'"),
    ),
)
def test_list_to_sql(value, expected_result):
    assert functions.list_to_sql(value) == expected_result


@pytest.mark.parametrize(
    'value,expected_result',
    (
        ('', '<w:r><w:t></w:t></w:r>'),
        ('HELLO', '<w:r><w:t>HELLO</w:t></w:r>'),
        ('<w:t>', '<w:t>'),
        (None, '<w:r><w:t></w:t></w:r>'),
    ),
)
def test_surround(value, expected_result):
    assert functions.surround(value) == expected_result


@pytest.mark.parametrize(
    'value,expected_result',
    (
        ('', ''),
        ('HELLO', ''),
        ('<xml><w:body>HEADER<w:sectPr>FOOTER</w:sectPr></w:body></xml>', 'HEADER'),
        ('<w:body>HEADER<w:sectPr>FOOTER</w:sectPr></w:body>', ''),
    ),

)
def test_remove_header_footer_xml(value, expected_result):
    assert functions.remove_header_footer_xml(value) == expected_result


@pytest.mark.parametrize(
    'value,expected_result',
    (
        ('', ''),
        ('HELLO', 'HELLO'),
        (' 1234,5678 ', ' 1234.5678 '),
        (' 1234,5678/', ' 1234.5678/'),
        (' 12,5678%', ' 12.5678%'),
        (' 12,5678 )', ' 12.5678 )'),
        (' 12,5678)', ' 12.5678)'),
        ('12,5678)', '12.5678)'),
        ('1,2%', '1.2%'),
        ('70 %', '70%'),
        ('10,2%', '10.2%'),
        ('20,2 Kg', '20.2 kg'),
        ('30,2Kg', '30.2kg'),

        ('40,2 kg', '40.2 kg'),
        ('50,2kg', '50.2kg'),

        ('40,2 g', '40.2 g'),
        ('50,2g', '50.2g'),

        ('40,2 m', '40.2 m'),
        ('50,2m', '50.2m'),

        ('40,2 C', '40.2 C'),
        ('40,123 dl', '40.123 dl'),
        ('40,2 decitex', '40.2 decitex'),
        ('40,2 kW', '40.2 kW'),
        ('40,2 W', '40.2 W'),
        ('40,2 V', '40.2 V'),
        ('40,2 Ah', '40.2 Ah'),
        ('40,2 bar', '40.2 bar'),
        ('40,2 cm', '40.2 cm'),
        ('40,2 Nm', '40.2 Nm'),
        ('40,2 kV', '40.2 kV'),

        ('40,2 MHz', '40.2 MHz'),
        ('40,2 μm', '40.2 μm'),
        ('40,2 Ohm', '40.2 Ohm'),
        ('40,2 dB', '40.2 dB'),
        ('40,2 kvar', '40.2 kvar'),
        ('±40,2', '±40.2'),
        ('€ 40,20', '€40.20'),
        ('€40,20', '€40.20'),
        ('€40.20', '€40.20'),
        ('€ 224', '€224'),
        (
            'Lithium metal of a purity by weight of 98,8 % or more (CAS RN 7439-93-2)',
            'Lithium metal of a purity by weight of 98.8% or more (CAS RN 7439-93-2)',
        ),
    ),
)
def test_apply_value_format_to_document(value, expected_result):
    assert functions.apply_value_format_to_document(value) == expected_result


@pytest.mark.parametrize(
    'value,expected_result',
    (
        (1, 1),
        (12345, 12345),
        ('12345', 12345),
        ('00005', 5),
        (None, 0),
        (True, 1),
        ('hello', 0),
        (f'{0:1}', 0)
    ),
)
def test_mnum(value, expected_result):
    assert functions.mnum(value) == expected_result


@pytest.mark.parametrize(
    'value,expected_result',
    (
        (1, '1'),
        (None, ''),
        (True, 'True'),
        ('hello', 'hello'),
        (f'{0:1}', '0'),
        ('1 EUR', '1 €'),
        ('1 EUR DTN G', '1 € / 100 kg gross'),
        ('1 EUR DTN', '1 € / 100 kg'),
        ('DTN G DTN', '/ 100 kg gross / 100 kg'),

    ),
)
def test_seasonal_expression(value, expected_result):
    assert functions.format_seasonal_expression(value) == expected_result


@mock.patch('zipfile.ZipFile.write')
def test_zipdir(mock_zip_file):
    mock_zip_file.return_value = None
    with tempfile.TemporaryDirectory() as temp_dir:
        with tempfile.NamedTemporaryFile(dir=temp_dir) as temp_file_2:
            temp_file = tempfile.NamedTemporaryFile()
            Path(f'{temp_dir}/.DS_Store').touch()
            functions.zipdir(temp_dir, temp_file)
    assert mock_zip_file.called
    assert mock_zip_file.call_count == 1
    directory_path, expected_file_name = os.path.split(temp_file_2.name)
    mock_zip_file.assert_called_once_with(temp_file_2.name, expected_file_name)
