from django.conf import settings


CLASSIFICATION = 'classification'
SCHEDULE = 'schedule'
CUCUMBER_COMMODITY_CODES = ["0707000510", "0707000520"]
BUS_TYRES_COMMODITY_CODES = ['8708701080', '8708701085', '8708701092', '8708701095']


GET_SECTION_CHAPTERS = """
SELECT LEFT(gn.goods_nomenclature_item_id, 2) as chapter, cs.section_id
FROM chapters_sections cs, goods_nomenclatures gn
WHERE cs.goods_nomenclature_sid = gn.goods_nomenclature_sid
AND gn.producline_suffix = '80'
ORDER BY 1
"""

GET_AUTHORISED_USE_COMMODITIES = """
SELECT DISTINCT goods_nomenclature_item_id FROM django.current_measures m WHERE measure_type_id = '105' ORDER BY 1;
"""

GET_CLASSIFICATIONS = """
SELECT DISTINCT goods_nomenclature_item_id, producline_suffix,
description, number_indents FROM django.goods_nomenclature_export_brexit('{chapter_string}%')
ORDER BY 1, 2"""


GET_SECTION_DETAILS = """
SELECT s.numeral, s.title, cs.section_id
FROM goods_nomenclatures gn, chapters_sections cs, sections s
WHERE gn.goods_nomenclature_sid = cs.goods_nomenclature_sid
AND s.id = cs.section_id
AND gn.goods_nomenclature_item_id = '{chapter_string}00000000'
"""


GET_DUTIES = f"""
SELECT m.goods_nomenclature_item_id, m.additional_code_type_id, m.additional_code_id,
m.measure_type_id, mc.duty_expression_id, mc.duty_amount, mc.monetary_unit_code,
mc.measurement_unit_code, mc.measurement_unit_qualifier_code, m.measure_sid /*,
m.validity_start_date, m.validity_end_date, m.geographical_area_id*/
FROM measure_components mc, django.measures_real_end_dates m
WHERE mc.measure_sid = m.measure_sid
AND LEFT(m.goods_nomenclature_item_id, 2) = '{{chapter_string}}'
AND m.measure_type_id IN ('103', '105')
and m.validity_start_date >= '{settings.BREXIT_DATE_STRING}'
ORDER BY m.goods_nomenclature_item_id, m.measure_type_id, m.measure_sid, mc.duty_expression_id
"""
