import pytest

from trade_tariff_reference.core.tests.utils import assert_xml
from trade_tariff_reference.documents.mfn.description import update_description

EXP_DESCRIPTION_1 = '<w:p><w:r/><w:r>' \
                    '<w:rPr>  ' \
                    '<w:i/>' \
                    '</w:rPr>' \
                    '<w:t>Latin</w:t>' \
                    '</w:r>' \
                    '<w:r/>' \
                    '</w:p>'

EXP_DESCRIPTION_2 = '<w:p><w:r/><w:r>' \
                    '<w:rPr>  ' \
                    '<w:b/>' \
                    '</w:rPr>' \
                    '<w:t>Bold</w:t>' \
                    '</w:r>' \
                    '<w:r/>' \
                    '</w:p>'

EXP_DESCRIPTION_3 = '<w:p><w:r/><w:r>' \
                    '<w:rPr>  ' \
                    '<w:u w:val="single"/>' \
                    '</w:rPr>' \
                    '<w:t>Underline</w:t>' \
                    '</w:r>' \
                    '<w:r/>' \
                    '</w:p>'

EXP_DESCRIPTION_4 = '<w:p><w:r>' \
                    '<w:t>Line break</w:t>' \
                    '</w:r>' \
                    '<w:r><w:br/></w:r>' \
                    '</w:p>'

EXP_DESCRIPTION_5 = '<w:p><w:r/><w:r/><w:r>' \
                    '<w:t xml:space="preserve">- </w:t>' \
                    '<w:t>Point 1</w:t>' \
                    '<w:br/>' \
                    '</w:r>' \
                    '<w:r/>' \
                    '<w:r>' \
                    '<w:t xml:space="preserve">- </w:t>' \
                    '<w:t>Point 2</w:t>' \
                    '<w:br/>' \
                    '</w:r>' \
                    '<w:r><w:br/></w:r>' \
                    '<w:r/>' \
                    '</w:p>'

EXP_DESCRIPTION_6 = '<w:p><w:r/><w:r>' \
                    '<w:rPr>  ' \
                    '<w:vertAlign w:val="superscript"/></w:rPr>' \
                    '<w:t>Superscript</w:t>' \
                    '</w:r>' \
                    '<w:r/>' \
                    '</w:p>'

EXP_DESCRIPTION_7 = '<w:p><w:r/><w:r>' \
                    '<w:rPr>  ' \
                    '<w:vertAlign w:val="subscript"/></w:rPr>' \
                    '<w:t>Subscript</w:t>' \
                    '</w:r>' \
                    '<w:r/>' \
                    '</w:p>'


@pytest.mark.parametrize(
    'description,expected_result',
    (
        ('<i>Latin</i>', EXP_DESCRIPTION_1),
        ('<b>Bold</b>', EXP_DESCRIPTION_2),
        ('<u>Underline</u>', EXP_DESCRIPTION_3),
        ('Line break<br>', EXP_DESCRIPTION_4),
        ('<ul><li>Point 1</li><li>Point 2</li></ul>', EXP_DESCRIPTION_5),
        ('<sup>Superscript</sup>', EXP_DESCRIPTION_6),
        ('<sub>Subscript</sub>', EXP_DESCRIPTION_7),
    )
)
def test_update_description(description, expected_result):
    actual_result = update_description(description)
    assert_xml(actual_result, expected_result)
