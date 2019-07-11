
GET_COMMODITIES_SQL = """
SELECT DISTINCT m.goods_nomenclature_item_id, m.validity_start_date,
 mc.condition_duty_amount, mc.condition_monetary_unit_code,
 mc.condition_measurement_unit_code
FROM ml.v5_2019 m, measure_conditions mc, measure_condition_components mcm
WHERE mc.measure_sid = m.measure_sid
AND mc.measure_condition_sid = mcm.measure_condition_sid
AND mc.condition_code = 'V' AND
 geographical_area_id IN ({geo_ids}) AND mcm.duty_amount != 0
ORDER BY 1, 2 DESC, 3 DESC
"""


GET_SECTIONS_CHAPTERS_SQL = """
SELECT LEFT(gn.goods_nomenclature_item_id, 2) as chapter, cs.section_id
FROM chapters_sections cs, goods_nomenclatures gn
WHERE cs.goods_nomenclature_sid = gn.goods_nomenclature_sid AND gn.producline_suffix = '80'
ORDER BY 1
"""

GET_MFNS_FOR_SIV_PRODUCTS_SQL = """
SELECT DISTINCT m.goods_nomenclature_item_id,
 mcc.duty_amount, m.validity_start_date, m.validity_end_date
FROM measures m, measure_conditions mc, measure_condition_components mcc
WHERE mcc.measure_condition_sid = mc.measure_condition_sid
AND m.measure_sid = mc.measure_sid
AND mcc.duty_expression_id = '01'
AND (m.validity_start_date > '2018-01-01')
AND mc.condition_code = 'V'
AND m.measure_type_id IN ('103', '105')
AND m.geographical_area_id = '1011'
ORDER BY m.goods_nomenclature_item_id, m.validity_start_date
"""


GET_MEUSRING_COMPONENTS_SQL = """
SELECT AVG(duty_amount)
FROM ml.meursing_components WHERE geographical_area_id = '1011'
"""


GET_MEUSRING_PERCENTAGE_SQL = """
SELECT AVG(duty_amount) FROM ml.meursing_components
 WHERE geographical_area_id = '{geographical_area_id}' AND
 reduction_indicator =  '{reduction_indicator}'
"""

CHECK_FOR_QUOTAS_SQL = """
SELECT DISTINCT ordernumber FROM ml.v5_2019 m WHERE m.measure_type_id IN ('143', '146')
AND m.geographical_area_id IN ({geo_ids}) ORDER BY 1
"""

GET_MEASURE_COMPONENTS_SQL = """
SELECT DISTINCT mc.measure_sid, mcc.duty_amount FROM measure_conditions mc,
measure_condition_components mcc, measures m
WHERE mc.measure_condition_sid = mcc.measure_condition_sid
AND m.measure_sid = mc.measure_sid AND condition_code = 'V' AND mcc.duty_expression_id = '01'
AND m.measure_type_id IN ({measure_type_list})
AND m.geographical_area_id IN ({geo_ids})
AND m.validity_start_date < '2019-12-31' AND m.validity_end_date >= '2018-01-01'
ORDER BY measure_sid;
"""

CHECK_COUNTRY_EXCLUSION_SQL = """
SELECT m.measure_sid FROM measure_excluded_geographical_areas mega, ml.v5_2019 m
WHERE m.measure_sid = mega.measure_sid
AND excluded_geographical_area = '{exclusion_check}'
ORDER BY validity_start_date DESC
"""

GET_DUTIES_SQL = """
SELECT DISTINCT m.goods_nomenclature_item_id, m.additional_code_type_id, m.additional_code_id,
m.measure_type_id, mc.duty_expression_id, mc.duty_amount, mc.monetary_unit_code,
mc.measurement_unit_code, mc.measurement_unit_qualifier_code, m.measure_sid, m.ordernumber,
m.validity_start_date, m.validity_end_date, m.geographical_area_id, m.reduction_indicator
FROM goods_nomenclatures gn, ml.v5_2019 m
LEFT OUTER JOIN measure_components mc ON m.measure_sid = mc.measure_sid
WHERE (m.measure_type_id IN ({measure_type_list})
AND m.geographical_area_id IN ({geo_ids})
AND m.goods_nomenclature_item_id = gn.goods_nomenclature_item_id
AND gn.validity_end_date IS NULL AND gn.producline_suffix = '80'
) ORDER BY m.goods_nomenclature_item_id, validity_start_date DESC, mc.duty_expression_id
"""

GET_QUOTA_ORDER_NUMBERS_SQL = """
SELECT DISTINCT ordernumber FROM ml.v5_2019 m WHERE m.measure_type_id IN ('143', '146')
AND m.geographical_area_id IN ({geo_ids}) ORDER BY 1
"""

GET_QUOTA_MEASURES_SQL = """
SELECT DISTINCT measure_sid, goods_nomenclature_item_id, ordernumber, validity_start_date,
validity_end_date, geographical_area_id, reduction_indicator FROM ml.v5_2019 m
WHERE measure_type_id IN ('143', '146') AND geographical_area_id IN ({geo_ids})
ORDER BY goods_nomenclature_item_id, measure_sid
"""

GET_QUOTA_DEFINITIONS_SQL = """
SELECT * FROM quota_definitions WHERE quota_order_number_id IN ({order_numbers})
AND validity_start_date >= '2018-01-01' ORDER BY quota_order_number_id, validity_start_date DESC
"""