-- -------------------------------------------------------------
-- Reference document database views
--
-- Generation Time: 2019-08-05 11:39:01.2810
-- -------------------------------------------------------------


CREATE SCHEMA IF NOT EXISTS "ml";

CREATE OR REPLACE FUNCTION ml.reformat_regulation_id(reg character varying)
 RETURNS character varying
 LANGUAGE plpgsql
AS $function$
declare
outreg character varying;
begin
select into outreg left(reg, 1) || right(reg, 4) || '/' || substring(reg, 2, 2);
return outreg;
end
$function$;


CREATE OR REPLACE VIEW "ml"."v5_2019" AS SELECT measures.measure_sid,
    ml.reformat_regulation_id(("left"((measures.measure_generating_regulation_id)::text, 7))::character varying) AS reformat_regulation_id,
    "left"((measures.measure_generating_regulation_id)::text, 7) AS regulation_id,
    (measures.measure_generating_regulation_id)::text AS regulation_id_full,
    measures.goods_nomenclature_item_id,
    measures.additional_code_type_id,
    measures.additional_code_id,
    measures.measure_type_id,
    measures.geographical_area_id,
    measures.validity_start_date,
    measures.validity_end_date,
    base_regulations.effective_end_date,
    measures.ordernumber,
    measures."national",
    measures.reduction_indicator,
    measures.measure_generating_regulation_role,
    measures.measure_generating_regulation_id,
    measures.justification_regulation_role,
    measures.justification_regulation_id,
    measures.stopped_flag,
    measures.geographical_area_sid,
    measures.goods_nomenclature_sid,
    measures.additional_code_sid,
    measures.export_refund_nomenclature_sid,
    base_regulations.regulation_group_id
   FROM measures,
    base_regulations
  WHERE (((measures.measure_generating_regulation_id)::text = (base_regulations.base_regulation_id)::text) AND (base_regulations.validity_start_date <= '2019-12-31 00:00:00'::timestamp without time zone) AND ((base_regulations.effective_end_date >= '2018-01-01 00:00:00'::timestamp without time zone) OR (((base_regulations.validity_end_date >= '2018-01-01 00:00:00'::timestamp without time zone) OR (base_regulations.validity_end_date IS NULL)) AND (base_regulations.effective_end_date IS NULL))) AND (base_regulations.explicit_abrogation_regulation_id IS NULL) AND (base_regulations.complete_abrogation_regulation_id IS NULL) AND ((measures.validity_end_date IS NULL) OR (measures.validity_end_date >= '2018-01-01 00:00:00'::timestamp without time zone)) AND (measures.validity_start_date <= '2019-12-31 00:00:00'::timestamp without time zone))
UNION
 SELECT measures.measure_sid,
    ml.reformat_regulation_id(("left"((measures.measure_generating_regulation_id)::text, 7))::character varying) AS reformat_regulation_id,
    "left"((measures.measure_generating_regulation_id)::text, 7) AS regulation_id,
    (measures.measure_generating_regulation_id)::text AS regulation_id_full,
    measures.goods_nomenclature_item_id,
    measures.additional_code_type_id,
    measures.additional_code_id,
    measures.measure_type_id,
    measures.geographical_area_id,
    measures.validity_start_date,
    measures.validity_end_date,
    modification_regulations.effective_end_date,
    measures.ordernumber,
    measures."national",
    measures.reduction_indicator,
    measures.measure_generating_regulation_role,
    measures.measure_generating_regulation_id,
    measures.justification_regulation_role,
    measures.justification_regulation_id,
    measures.stopped_flag,
    measures.geographical_area_sid,
    measures.goods_nomenclature_sid,
    measures.additional_code_sid,
    measures.export_refund_nomenclature_sid,
    base_regulations.regulation_group_id
   FROM measures,
    (modification_regulations
     LEFT JOIN base_regulations ON (((modification_regulations.base_regulation_id)::text = (base_regulations.base_regulation_id)::text)))
  WHERE (((measures.measure_generating_regulation_id)::text = (modification_regulations.modification_regulation_id)::text) AND (modification_regulations.validity_start_date <= '2019-12-31 00:00:00'::timestamp without time zone) AND ((modification_regulations.effective_end_date >= '2018-01-01 00:00:00'::timestamp without time zone) OR (((modification_regulations.validity_end_date >= '2018-01-01 00:00:00'::timestamp without time zone) OR (modification_regulations.validity_end_date IS NULL)) AND (modification_regulations.effective_end_date IS NULL))) AND (modification_regulations.complete_abrogation_regulation_id IS NULL) AND (modification_regulations.explicit_abrogation_regulation_id IS NULL) AND ((measures.validity_end_date IS NULL) OR (measures.validity_end_date >= '2018-01-01 00:00:00'::timestamp without time zone)) AND (measures.validity_start_date <= '2019-12-31 00:00:00'::timestamp without time zone))
  ORDER BY 1, 2, 3, 4;


CREATE OR REPLACE VIEW "ml"."meursing_components" AS SELECT m.measure_sid,
    m.measure_type_id,
    m.additional_code_id,
    mc.duty_amount,
    m.validity_start_date,
    m.validity_end_date,
    m.geographical_area_id,
    m.reduction_indicator
   FROM measures m,
    measure_components mc,
    base_regulations r
  WHERE ((m.measure_sid = mc.measure_sid) AND ((m.measure_generating_regulation_id)::text = (r.base_regulation_id)::text) AND (m.additional_code_type_id = '7'::text) AND (m.validity_end_date IS NULL) AND (r.validity_end_date IS NULL))
UNION
 SELECT m.measure_sid,
    m.measure_type_id,
    m.additional_code_id,
    mc.duty_amount,
    m.validity_start_date,
    m.validity_end_date,
    m.geographical_area_id,
    m.reduction_indicator
   FROM measures m,
    measure_components mc,
    modification_regulations r
  WHERE ((m.measure_sid = mc.measure_sid) AND ((m.measure_generating_regulation_id)::text = (r.modification_regulation_id)::text) AND (m.additional_code_type_id = '7'::text) AND (m.validity_end_date IS NULL) AND (r.validity_end_date IS NULL))
  ORDER BY 2, 3, 5 DESC;
