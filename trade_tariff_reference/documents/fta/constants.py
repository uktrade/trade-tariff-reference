from django.conf import settings


NUMBER_OF_DAYS_PER_YEAR = 365
INFINITE_MEASURE_EXTENT = -1

PUBLISHED = 'published'

FIRST_COME_FIRST_SERVED = 'FCFS'


GET_COMMODITIES_SQL = """
SELECT DISTINCT m.goods_nomenclature_item_id,
m.validity_start_date,
mc.condition_duty_amount,
mc.condition_monetary_unit_code,
mc.condition_measurement_unit_code
FROM ml.v5_2019 m,
measure_conditions mc,
measure_condition_components mcc
WHERE mc.measure_sid = m.measure_sid
AND mc.measure_condition_sid = mcc.measure_condition_sid
AND mc.condition_code = 'V'
AND mc.status = 'published'
AND mcc.status = 'published'
AND geographical_area_id IN ({geo_ids}) AND mcc.duty_amount != 0
ORDER BY 1, 2 DESC, 3 DESC
"""


GET_SECTIONS_CHAPTERS_SQL = """
SELECT LEFT(gn.goods_nomenclature_item_id, 2) as chapter,
cs.section_id
FROM chapters_sections cs,
goods_nomenclatures gn
WHERE cs.goods_nomenclature_sid = gn.goods_nomenclature_sid
AND gn.status = 'published'
AND gn.producline_suffix = '80'
ORDER BY 1
"""

GET_MFNS_FOR_SIV_PRODUCTS_SQL = f"""
SELECT DISTINCT m.goods_nomenclature_item_id,
mcc.duty_amount,
m.validity_start_date,
m.validity_end_date
FROM measures m,
measure_conditions mc,
measure_condition_components mcc
WHERE mcc.measure_condition_sid = mc.measure_condition_sid
    AND m.status = 'published'
    AND mc.status = 'published'
    AND mcc.status = 'published'
    AND m.measure_sid = mc.measure_sid
    AND mcc.duty_expression_id = '01'
    AND (m.validity_start_date > '{settings.BREXIT_VALIDITY_START_DATE_STRING}')
    AND mc.condition_code = 'V'
    AND m.measure_type_id IN ('103', '105')
    AND m.geographical_area_id = '1011'
ORDER BY m.goods_nomenclature_item_id, m.validity_start_date
"""


GET_MEUSRING_COMPONENTS_DUTY_AVERAGE_SQL = """
SELECT AVG(duty_amount)
FROM ml.meursing_components
WHERE geographical_area_id = '1011'
"""


GET_MEUSRING_PERCENTAGE_SQL = """
SELECT AVG(duty_amount)
FROM ml.meursing_components
WHERE geographical_area_id = '{geographical_area_id}'
AND reduction_indicator = '{reduction_indicator}'
"""


GET_MEASURE_COMPONENTS_SQL = f"""
SELECT DISTINCT mc.measure_sid,
mcc.duty_amount
FROM measure_conditions mc,
measure_condition_components mcc,
measures m
WHERE mc.measure_condition_sid = mcc.measure_condition_sid
    AND m.status = 'published'
    AND mc.status = 'published'
    AND mcc.status = 'published'
    AND m.measure_sid = mc.measure_sid AND condition_code = 'V' AND mcc.duty_expression_id = '01'
    AND m.measure_type_id IN ({{measure_type_list}})
    AND m.geographical_area_id IN ({{geo_ids}})
    AND m.validity_start_date < '{settings.BREXIT_VALIDITY_END_DATE_STRING}'
    AND m.validity_end_date >= '{settings.BREXIT_VALIDITY_START_DATE_STRING}'
ORDER BY measure_sid;
"""

GET_DUTIES_SQL = """
SELECT DISTINCT m.goods_nomenclature_item_id,
m.additional_code_type_id,
m.additional_code_id,
m.measure_type_id,
mc.duty_expression_id,
mc.duty_amount,
mc.monetary_unit_code,
mc.measurement_unit_code,
mc.measurement_unit_qualifier_code,
m.measure_sid,
m.ordernumber,
m.validity_start_date,
m.validity_end_date,
m.geographical_area_id,
m.reduction_indicator
FROM goods_nomenclatures gn,
ml.v5_2019 m
LEFT OUTER JOIN measure_components mc ON m.measure_sid = mc.measure_sid
WHERE (
    m.measure_type_id IN ({measure_type_list})
    AND gn.status = 'published'
    AND m.geographical_area_id IN ({geo_ids})
    AND m.goods_nomenclature_item_id = gn.goods_nomenclature_item_id
    AND gn.validity_end_date IS NULL AND gn.producline_suffix = '80'
)
ORDER BY m.goods_nomenclature_item_id, validity_start_date DESC, mc.duty_expression_id
"""

GET_QUOTA_ORDER_NUMBERS_SQL = """
SELECT DISTINCT ordernumber
FROM ml.v5_2019 m
WHERE m.measure_type_id IN ('143', '146')
AND m.geographical_area_id IN ({geo_ids}) ORDER BY 1
"""


GET_QUOTA_MEASURES_SQL = """
SELECT DISTINCT measure_sid,
goods_nomenclature_item_id,
ordernumber,
validity_start_date,
validity_end_date,
geographical_area_id,
reduction_indicator
FROM ml.v5_2019 m
WHERE measure_type_id IN ('143', '146') AND geographical_area_id IN ({geo_ids})
ORDER BY goods_nomenclature_item_id, measure_sid
"""

# TODO: MPP set validity date to 2019-01-01
# if quotas are not appearing instead of settings.BREXIT_VALIDITY_START_DATE_STRING
GET_QUOTA_DEFINITIONS_SQL = f"""
SELECT * FROM quota_definitions
WHERE quota_order_number_id IN ({{order_numbers}})
AND status = 'published'
AND validity_start_date >= '{settings.BREXIT_VALIDITY_START_DATE_STRING}'
ORDER BY quota_order_number_id, validity_start_date DESC
"""

# TODO: MPP set validity date to 2019-11-01 to find all quota balances
FIRST_QUOTA_BALANCE_OF_THE_YEAR_SQL = """
SELECT quota_order_number_id,
MIN(validity_start_date) as min_start
FROM quota_definitions
WHERE status ='published'
AND (
(validity_start_date >= '2020-01-01' AND validity_start_date <= '2020-12-31')
OR
(validity_end_date >= '2020-01-01' AND validity_end_date <= '2020-12-31')
)
GROUP BY quota_order_number_id
"""


GET_QUOTA_BALANCE_SQL = f"""
SELECT qd.quota_order_number_id,
qd.measurement_unit_code,
qd.initial_volume,
qd.volume,
qd.description,
qd.validity_start_date,
qd.validity_end_date,
qd.quota_definition_sid
FROM ({FIRST_QUOTA_BALANCE_OF_THE_YEAR_SQL}) self JOIN quota_definitions qd
ON qd.quota_order_number_id = self.quota_order_number_id
AND self.min_start = qd.validity_start_date
INNER JOIN quota_order_number_origins qo
ON qd.quota_order_number_sid = qo.quota_order_number_sid
AND qo.geographical_area_id IN ({{geo_ids}})
ORDER BY qd.quota_order_number_id
"""
