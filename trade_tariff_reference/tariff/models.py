# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AdditionalCodeDescriptionPeriods(models.Model):
    additional_code_description_period_sid = models.IntegerField(blank=True, null=True)
    additional_code_sid = models.IntegerField(blank=True, null=True)
    additional_code_type_id = models.CharField(max_length=1, blank=True, null=True)
    additional_code = models.CharField(max_length=3, blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)
    added_by_id = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'additional_code_description_periods'


class AdditionalCodeDescriptions(models.Model):
    additional_code_description_period_sid = models.IntegerField(blank=True, null=True)
    language_id = models.CharField(max_length=5, blank=True, null=True)
    additional_code_sid = models.IntegerField(blank=True, null=True)
    additional_code_type_id = models.CharField(max_length=1, blank=True, null=True)
    additional_code = models.CharField(max_length=3, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)
    added_by_id = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'additional_code_descriptions'


class AdditionalCodeTypeDescriptions(models.Model):
    additional_code_type_id = models.CharField(max_length=1, blank=True, null=True)
    language_id = models.CharField(max_length=5, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'additional_code_type_descriptions'


class AdditionalCodeTypeMeasureTypes(models.Model):
    measure_type_id = models.CharField(max_length=3, blank=True, null=True)
    additional_code_type_id = models.CharField(max_length=1, blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'additional_code_type_measure_types'


class AdditionalCodeTypes(models.Model):
    additional_code_type_id = models.CharField(max_length=1, blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    application_code = models.CharField(max_length=255, blank=True, null=True)
    meursing_table_plan_id = models.CharField(max_length=2, blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'additional_code_types'


class AdditionalCodes(models.Model):
    additional_code_sid = models.IntegerField(blank=True, null=True)
    additional_code_type_id = models.CharField(max_length=1, blank=True, null=True)
    additional_code = models.CharField(max_length=3, blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)
    added_by_id = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'additional_codes'


class AllAdditionalCodes(models.Model):
    additional_code_sid = models.IntegerField(blank=True, null=True)
    additional_code_type_id = models.CharField(max_length=20, blank=True, null=True)
    additional_code = models.CharField(max_length=3, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    language_id = models.CharField(max_length=20, blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    added_by_id = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'all_additional_codes'


class BaseRegulations(models.Model):
    base_regulation_role = models.IntegerField(blank=True, null=True)
    base_regulation_id = models.CharField(max_length=255, blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    community_code = models.IntegerField(blank=True, null=True)
    regulation_group_id = models.CharField(max_length=255, blank=True, null=True)
    replacement_indicator = models.IntegerField(blank=True, null=True)
    stopped_flag = models.BooleanField(blank=True, null=True)
    information_text = models.TextField(blank=True, null=True)
    approved_flag = models.BooleanField(blank=True, null=True)
    published_date = models.DateField(blank=True, null=True)
    officialjournal_number = models.CharField(max_length=255, blank=True, null=True)
    officialjournal_page = models.IntegerField(blank=True, null=True)
    effective_end_date = models.DateTimeField(blank=True, null=True)
    antidumping_regulation_role = models.IntegerField(blank=True, null=True)
    related_antidumping_regulation_id = models.CharField(max_length=255, blank=True, null=True)
    complete_abrogation_regulation_role = models.IntegerField(blank=True, null=True)
    complete_abrogation_regulation_id = models.CharField(max_length=255, blank=True, null=True)
    explicit_abrogation_regulation_role = models.IntegerField(blank=True, null=True)
    explicit_abrogation_regulation_id = models.CharField(max_length=255, blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    added_by_id = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'base_regulations'


class CertificateDescriptionPeriods(models.Model):
    certificate_description_period_sid = models.IntegerField(blank=True, null=True)
    certificate_type_code = models.CharField(max_length=1, blank=True, null=True)
    certificate_code = models.CharField(max_length=3, blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)
    added_by_id = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'certificate_description_periods'


class CertificateDescriptions(models.Model):
    certificate_description_period_sid = models.IntegerField(blank=True, null=True)
    language_id = models.CharField(max_length=5, blank=True, null=True)
    certificate_type_code = models.CharField(max_length=1, blank=True, null=True)
    certificate_code = models.CharField(max_length=3, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)
    added_by_id = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'certificate_descriptions'


class CertificateTypeDescriptions(models.Model):
    certificate_type_code = models.CharField(max_length=1, blank=True, null=True)
    language_id = models.CharField(max_length=5, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'certificate_type_descriptions'


class CertificateTypes(models.Model):
    certificate_type_code = models.CharField(max_length=1, blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'certificate_types'


class Certificates(models.Model):
    certificate_type_code = models.CharField(max_length=1, blank=True, null=True)
    certificate_code = models.CharField(max_length=3, blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    national_abbrev = models.TextField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)
    added_by_id = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'certificates'


class CompleteAbrogationRegulations(models.Model):
    complete_abrogation_regulation_role = models.IntegerField(blank=True, null=True)
    complete_abrogation_regulation_id = models.CharField(max_length=255, blank=True, null=True)
    published_date = models.DateField(blank=True, null=True)
    officialjournal_number = models.CharField(max_length=255, blank=True, null=True)
    officialjournal_page = models.IntegerField(blank=True, null=True)
    replacement_indicator = models.IntegerField(blank=True, null=True)
    information_text = models.TextField(blank=True, null=True)
    approved_flag = models.BooleanField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    added_by_id = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'complete_abrogation_regulations'


class DutyExpressionDescriptions(models.Model):
    duty_expression_id = models.CharField(max_length=255, blank=True, null=True)
    language_id = models.CharField(max_length=5, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'duty_expression_descriptions'


class DutyExpressions(models.Model):
    duty_expression_id = models.CharField(max_length=255, blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    duty_amount_applicability_code = models.IntegerField(blank=True, null=True)
    measurement_unit_applicability_code = models.IntegerField(blank=True, null=True)
    monetary_unit_applicability_code = models.IntegerField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'duty_expressions'


class ExplicitAbrogationRegulations(models.Model):
    explicit_abrogation_regulation_role = models.IntegerField(blank=True, null=True)
    explicit_abrogation_regulation_id = models.CharField(max_length=8, blank=True, null=True)
    published_date = models.DateField(blank=True, null=True)
    officialjournal_number = models.CharField(max_length=255, blank=True, null=True)
    officialjournal_page = models.IntegerField(blank=True, null=True)
    replacement_indicator = models.IntegerField(blank=True, null=True)
    abrogation_date = models.DateField(blank=True, null=True)
    information_text = models.TextField(blank=True, null=True)
    approved_flag = models.BooleanField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    added_by_id = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'explicit_abrogation_regulations'


class ExportRefundNomenclatureDescriptionPeriods(models.Model):
    export_refund_nomenclature_description_period_sid = models.IntegerField(blank=True, null=True)
    export_refund_nomenclature_sid = models.IntegerField(blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    goods_nomenclature_item_id = models.CharField(max_length=10, blank=True, null=True)
    additional_code_type = models.TextField(blank=True, null=True)
    export_refund_code = models.CharField(max_length=255, blank=True, null=True)
    productline_suffix = models.CharField(max_length=2, blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'export_refund_nomenclature_description_periods'


class ExportRefundNomenclatureDescriptions(models.Model):
    export_refund_nomenclature_description_period_sid = models.IntegerField(blank=True, null=True)
    language_id = models.CharField(max_length=5, blank=True, null=True)
    export_refund_nomenclature_sid = models.IntegerField(blank=True, null=True)
    goods_nomenclature_item_id = models.CharField(max_length=10, blank=True, null=True)
    additional_code_type = models.TextField(blank=True, null=True)
    export_refund_code = models.CharField(max_length=255, blank=True, null=True)
    productline_suffix = models.CharField(max_length=2, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'export_refund_nomenclature_descriptions'


class ExportRefundNomenclatureIndents(models.Model):
    export_refund_nomenclature_indents_sid = models.IntegerField(blank=True, null=True)
    export_refund_nomenclature_sid = models.IntegerField(blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    number_export_refund_nomenclature_indents = models.IntegerField(blank=True, null=True)
    goods_nomenclature_item_id = models.CharField(max_length=10, blank=True, null=True)
    additional_code_type = models.TextField(blank=True, null=True)
    export_refund_code = models.CharField(max_length=255, blank=True, null=True)
    productline_suffix = models.CharField(max_length=2, blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'export_refund_nomenclature_indents'


class ExportRefundNomenclatures(models.Model):
    export_refund_nomenclature_sid = models.IntegerField(blank=True, null=True)
    goods_nomenclature_item_id = models.CharField(max_length=10, blank=True, null=True)
    additional_code_type = models.CharField(max_length=1, blank=True, null=True)
    export_refund_code = models.CharField(max_length=3, blank=True, null=True)
    productline_suffix = models.CharField(max_length=2, blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    goods_nomenclature_sid = models.IntegerField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'export_refund_nomenclatures'


class FootnoteAssociationAdditionalCodes(models.Model):
    additional_code_sid = models.IntegerField(blank=True, null=True)
    footnote_type_id = models.CharField(max_length=2, blank=True, null=True)
    footnote_id = models.CharField(max_length=5, blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    additional_code_type_id = models.TextField(blank=True, null=True)
    additional_code = models.CharField(max_length=3, blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'footnote_association_additional_codes'


class FootnoteAssociationErns(models.Model):
    export_refund_nomenclature_sid = models.IntegerField(blank=True, null=True)
    footnote_type = models.CharField(max_length=2, blank=True, null=True)
    footnote_id = models.CharField(max_length=5, blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    goods_nomenclature_item_id = models.CharField(max_length=10, blank=True, null=True)
    additional_code_type = models.TextField(blank=True, null=True)
    export_refund_code = models.CharField(max_length=255, blank=True, null=True)
    productline_suffix = models.CharField(max_length=2, blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'footnote_association_erns'


class FootnoteAssociationGoodsNomenclatures(models.Model):
    goods_nomenclature_sid = models.IntegerField(blank=True, null=True)
    footnote_type = models.CharField(max_length=2, blank=True, null=True)
    footnote_id = models.CharField(max_length=5, blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    goods_nomenclature_item_id = models.CharField(max_length=10, blank=True, null=True)
    productline_suffix = models.CharField(max_length=2, blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)
    added_by_id = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'footnote_association_goods_nomenclatures'


class FootnoteAssociationMeasures(models.Model):
    measure_sid = models.IntegerField(blank=True, null=True)
    footnote_type_id = models.CharField(max_length=2, blank=True, null=True)
    footnote_id = models.CharField(max_length=5, blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    added_by_id = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'footnote_association_measures'


class FootnoteAssociationMeursingHeadings(models.Model):
    meursing_table_plan_id = models.CharField(max_length=2, blank=True, null=True)
    meursing_heading_number = models.CharField(max_length=255, blank=True, null=True)
    row_column_code = models.IntegerField(blank=True, null=True)
    footnote_type = models.CharField(max_length=2, blank=True, null=True)
    footnote_id = models.CharField(max_length=5, blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'footnote_association_meursing_headings'


class FootnoteDescriptionPeriods(models.Model):
    footnote_description_period_sid = models.IntegerField(blank=True, null=True)
    footnote_type_id = models.CharField(max_length=2, blank=True, null=True)
    footnote_id = models.CharField(max_length=5, blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    added_by_id = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'footnote_description_periods'


class FootnoteDescriptions(models.Model):
    footnote_description_period_sid = models.IntegerField(blank=True, null=True)
    footnote_type_id = models.CharField(max_length=2, blank=True, null=True)
    footnote_id = models.CharField(max_length=5, blank=True, null=True)
    language_id = models.CharField(max_length=5, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    added_by_id = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'footnote_descriptions'


class FootnoteTypeDescriptions(models.Model):
    footnote_type_id = models.CharField(max_length=2, blank=True, null=True)
    language_id = models.CharField(max_length=5, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'footnote_type_descriptions'


class FootnoteTypes(models.Model):
    footnote_type_id = models.CharField(max_length=2, blank=True, null=True)
    application_code = models.IntegerField(blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'footnote_types'


class Footnotes(models.Model):
    footnote_id = models.CharField(max_length=5, blank=True, null=True)
    footnote_type_id = models.CharField(max_length=2, blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    added_by_id = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'footnotes'


class FtsRegulationActions(models.Model):
    fts_regulation_role = models.IntegerField(blank=True, null=True)
    fts_regulation_id = models.CharField(max_length=8, blank=True, null=True)
    stopped_regulation_role = models.IntegerField(blank=True, null=True)
    stopped_regulation_id = models.CharField(max_length=8, blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'fts_regulation_actions'


class FullTemporaryStopRegulations(models.Model):
    full_temporary_stop_regulation_role = models.IntegerField(blank=True, null=True)
    full_temporary_stop_regulation_id = models.CharField(max_length=8, blank=True, null=True)
    published_date = models.DateField(blank=True, null=True)
    officialjournal_number = models.CharField(max_length=255, blank=True, null=True)
    officialjournal_page = models.IntegerField(blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    effective_enddate = models.DateField(blank=True, null=True)
    explicit_abrogation_regulation_role = models.IntegerField(blank=True, null=True)
    explicit_abrogation_regulation_id = models.CharField(max_length=8, blank=True, null=True)
    replacement_indicator = models.IntegerField(blank=True, null=True)
    information_text = models.TextField(blank=True, null=True)
    approved_flag = models.BooleanField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    added_by_id = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)
    complete_abrogation_regulation_role = models.IntegerField(blank=True, null=True)
    complete_abrogation_regulation_id = models.TextField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'full_temporary_stop_regulations'


class GeographicalAreaDescriptionPeriods(models.Model):
    geographical_area_description_period_sid = models.IntegerField(blank=True, null=True)
    geographical_area_sid = models.IntegerField(blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    geographical_area_id = models.CharField(max_length=255, blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)
    added_by_id = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'geographical_area_description_periods'


class GeographicalAreaDescriptions(models.Model):
    geographical_area_description_period_sid = models.IntegerField(blank=True, null=True)
    language_id = models.CharField(max_length=5, blank=True, null=True)
    geographical_area_sid = models.IntegerField(blank=True, null=True)
    geographical_area_id = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)
    added_by_id = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'geographical_area_descriptions'


class GeographicalAreaMemberships(models.Model):
    geographical_area_sid = models.IntegerField(blank=True, null=True)
    geographical_area_group_sid = models.IntegerField(blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)
    added_by_id = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'geographical_area_memberships'


class GeographicalAreas(models.Model):
    id = models.IntegerField(primary_key=True, db_column='geographical_area_sid')
    parent_geographical_area_group_sid = models.IntegerField(blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    geographical_code = models.CharField(max_length=255, blank=True, null=True)
    geographical_area_id = models.CharField(max_length=255, blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)
    added_by_id = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'geographical_areas'


class GoodsNomenclatureDescriptionPeriods(models.Model):
    goods_nomenclature_description_period_sid = models.IntegerField(blank=True, null=True)
    goods_nomenclature_sid = models.IntegerField(blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    goods_nomenclature_item_id = models.CharField(max_length=10, blank=True, null=True)
    productline_suffix = models.CharField(max_length=2, blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'goods_nomenclature_description_periods'


class GoodsNomenclatureDescriptions(models.Model):
    goods_nomenclature_description_period_sid = models.IntegerField(blank=True, null=True)
    language_id = models.CharField(max_length=5, blank=True, null=True)
    goods_nomenclature_sid = models.IntegerField(blank=True, null=True)
    goods_nomenclature_item_id = models.CharField(max_length=10, blank=True, null=True)
    productline_suffix = models.CharField(max_length=2, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'goods_nomenclature_descriptions'


class GoodsNomenclatureGroupDescriptions(models.Model):
    goods_nomenclature_group_type = models.CharField(max_length=1, blank=True, null=True)
    goods_nomenclature_group_id = models.CharField(max_length=6, blank=True, null=True)
    language_id = models.CharField(max_length=5, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'goods_nomenclature_group_descriptions'


class GoodsNomenclatureGroups(models.Model):
    goods_nomenclature_group_type = models.CharField(max_length=1, blank=True, null=True)
    goods_nomenclature_group_id = models.CharField(max_length=6, blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    nomenclature_group_facility_code = models.IntegerField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'goods_nomenclature_groups'


class GoodsNomenclatureIndents(models.Model):
    goods_nomenclature_indent_sid = models.IntegerField(blank=True, null=True)
    goods_nomenclature_sid = models.IntegerField(blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    number_indents = models.IntegerField(blank=True, null=True)
    goods_nomenclature_item_id = models.CharField(max_length=10, blank=True, null=True)
    productline_suffix = models.CharField(max_length=2, blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'goods_nomenclature_indents'


class GoodsNomenclatureOrigins(models.Model):
    goods_nomenclature_sid = models.IntegerField(blank=True, null=True)
    derived_goods_nomenclature_item_id = models.CharField(max_length=10, blank=True, null=True)
    derived_productline_suffix = models.CharField(max_length=2, blank=True, null=True)
    goods_nomenclature_item_id = models.CharField(max_length=10, blank=True, null=True)
    productline_suffix = models.CharField(max_length=2, blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'goods_nomenclature_origins'


class GoodsNomenclatureSuccessors(models.Model):
    goods_nomenclature_sid = models.IntegerField(blank=True, null=True)
    absorbed_goods_nomenclature_item_id = models.CharField(max_length=10, blank=True, null=True)
    absorbed_productline_suffix = models.CharField(max_length=2, blank=True, null=True)
    goods_nomenclature_item_id = models.CharField(max_length=10, blank=True, null=True)
    productline_suffix = models.CharField(max_length=2, blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'goods_nomenclature_successors'


class GoodsNomenclatures(models.Model):
    id = models.IntegerField(primary_key=True, db_column='goods_nomenclature_sid')
    goods_nomenclature_item_id = models.CharField(max_length=10, blank=True, null=True)
    producline_suffix = models.CharField(max_length=255, blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    statistical_indicator = models.IntegerField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'goods_nomenclatures'


class LanguageDescriptions(models.Model):
    language_code_id = models.CharField(max_length=255, blank=True, null=True)
    language_id = models.CharField(max_length=5, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'language_descriptions'


class Languages(models.Model):
    language_id = models.CharField(max_length=5, blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'languages'


class MeasureActionDescriptions(models.Model):
    action_code = models.CharField(max_length=255, blank=True, null=True)
    language_id = models.CharField(max_length=5, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'measure_action_descriptions'


class MeasureActions(models.Model):
    action_code = models.CharField(max_length=255, blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'measure_actions'


class MeasureComponents(models.Model):
    measure_sid = models.IntegerField(blank=True, null=True)
    duty_expression_id = models.CharField(max_length=255, blank=True, null=True)
    duty_amount = models.FloatField(blank=True, null=True)
    monetary_unit_code = models.CharField(max_length=255, blank=True, null=True)
    measurement_unit_code = models.CharField(max_length=3, blank=True, null=True)
    measurement_unit_qualifier_code = models.CharField(max_length=1, blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    added_by_id = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)
    original_duty_expression_id = models.TextField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'measure_components'


class MeasureConditionCodeDescriptions(models.Model):
    condition_code = models.CharField(max_length=255, blank=True, null=True)
    language_id = models.CharField(max_length=5, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'measure_condition_code_descriptions'


class MeasureConditionCodes(models.Model):
    condition_code = models.CharField(max_length=255, blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'measure_condition_codes'


class MeasureConditionComponents(models.Model):
    measure_condition_sid = models.IntegerField(blank=True, null=True)
    duty_expression_id = models.CharField(max_length=255, blank=True, null=True)
    duty_amount = models.FloatField(blank=True, null=True)
    monetary_unit_code = models.CharField(max_length=255, blank=True, null=True)
    measurement_unit_code = models.CharField(max_length=3, blank=True, null=True)
    measurement_unit_qualifier_code = models.CharField(max_length=1, blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    added_by_id = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)
    original_duty_expression_id = models.TextField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'measure_condition_components'


class MeasureConditions(models.Model):
    measure_condition_sid = models.IntegerField(blank=True, null=True)
    measure_sid = models.IntegerField(blank=True, null=True)
    condition_code = models.CharField(max_length=255, blank=True, null=True)
    component_sequence_number = models.IntegerField(blank=True, null=True)
    condition_duty_amount = models.FloatField(blank=True, null=True)
    condition_monetary_unit_code = models.CharField(max_length=255, blank=True, null=True)
    condition_measurement_unit_code = models.CharField(max_length=3, blank=True, null=True)
    condition_measurement_unit_qualifier_code = models.CharField(max_length=1, blank=True, null=True)
    action_code = models.CharField(max_length=255, blank=True, null=True)
    certificate_type_code = models.CharField(max_length=1, blank=True, null=True)
    certificate_code = models.CharField(max_length=3, blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    added_by_id = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)
    original_measure_condition_code = models.TextField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'measure_conditions'


class MeasureExcludedGeographicalAreas(models.Model):
    measure_sid = models.IntegerField(blank=True, null=True)
    excluded_geographical_area = models.CharField(max_length=255, blank=True, null=True)
    geographical_area_sid = models.IntegerField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    added_by_id = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'measure_excluded_geographical_areas'


class MeasurePartialTemporaryStops(models.Model):
    measure_sid = models.IntegerField(blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    partial_temporary_stop_regulation_id = models.CharField(max_length=255, blank=True, null=True)
    partial_temporary_stop_regulation_officialjournal_number = models.CharField(max_length=255, blank=True, null=True)
    partial_temporary_stop_regulation_officialjournal_page = models.IntegerField(blank=True, null=True)
    abrogation_regulation_id = models.CharField(max_length=255, blank=True, null=True)
    abrogation_regulation_officialjournal_number = models.CharField(max_length=255, blank=True, null=True)
    abrogation_regulation_officialjournal_page = models.IntegerField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'measure_partial_temporary_stops'


class MeasureTypeDescriptions(models.Model):
    measure_type_id = models.CharField(max_length=3, blank=True, null=True)
    language_id = models.CharField(max_length=5, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'measure_type_descriptions'


class MeasureTypeSeries(models.Model):
    measure_type_series_id = models.CharField(max_length=255, blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    measure_type_combination = models.IntegerField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'measure_type_series'


class MeasureTypeSeriesDescriptions(models.Model):
    measure_type_series_id = models.CharField(max_length=255, blank=True, null=True)
    language_id = models.CharField(max_length=5, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'measure_type_series_descriptions'


class MeasureTypes(models.Model):
    id = models.CharField(max_length=3, primary_key=True, db_column='measure_type_id')
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    trade_movement_code = models.IntegerField(blank=True, null=True)
    priority_code = models.IntegerField(blank=True, null=True)
    measure_component_applicable_code = models.IntegerField(blank=True, null=True)
    origin_dest_code = models.IntegerField(blank=True, null=True)
    order_number_capture_code = models.IntegerField(blank=True, null=True)
    measure_explosion_level = models.IntegerField(blank=True, null=True)
    measure_type_series_id = models.CharField(max_length=255, blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    measure_type_acronym = models.CharField(max_length=3, blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'measure_types'


class MeasurementUnitDescriptions(models.Model):
    measurement_unit_code = models.CharField(max_length=3, blank=True, null=True)
    language_id = models.CharField(max_length=5, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'measurement_unit_descriptions'


class MeasurementUnitQualifierDescriptions(models.Model):
    measurement_unit_qualifier_code = models.CharField(max_length=1, blank=True, null=True)
    language_id = models.CharField(max_length=5, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'measurement_unit_qualifier_descriptions'


class MeasurementUnitQualifiers(models.Model):
    measurement_unit_qualifier_code = models.CharField(max_length=1, blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'measurement_unit_qualifiers'


class MeasurementUnits(models.Model):
    measurement_unit_code = models.CharField(max_length=3, blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'measurement_units'


class Measurements(models.Model):
    measurement_unit_code = models.CharField(max_length=3, blank=True, null=True)
    measurement_unit_qualifier_code = models.CharField(max_length=1, blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'measurements'


class Measures(models.Model):
    measure_sid = models.IntegerField(primary_key=True)
    measure_type = models.ForeignKey(
        'tariff.MeasureTypes',
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )

    geographical_area = models.ForeignKey(
        'tariff.GeographicalAreas',
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        db_column='geographical_area_sid',
    )

    goods_nomenclature = models.ForeignKey(
        'tariff.GoodsNomenclatures',
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        db_column='goods_nomenclature_sid',
    )

    additional_code_sid = models.IntegerField(blank=True, null=True)

    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    measure_generating_regulation_role = models.IntegerField(blank=True, null=True)
    measure_generating_regulation_id = models.CharField(max_length=255, blank=True, null=True)
    justification_regulation_role = models.IntegerField(blank=True, null=True)
    justification_regulation_id = models.CharField(max_length=255, blank=True, null=True)
    stopped_flag = models.BooleanField(blank=True, null=True)

    ordernumber = models.CharField(max_length=255, blank=True, null=True)
    additional_code_type_id = models.TextField(blank=True, null=True)

    reduction_indicator = models.IntegerField(blank=True, null=True)
    export_refund_nomenclature_sid = models.IntegerField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    tariff_measure_number = models.CharField(max_length=10, blank=True, null=True)
    invalidated_by = models.IntegerField(blank=True, null=True)
    invalidated_at = models.DateTimeField(blank=True, null=True)

    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    added_by_id = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    last_status_change_at = models.DateTimeField(blank=True, null=True)
    last_update_by_id = models.IntegerField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    searchable_data = models.TextField(blank=True, null=True)  # This field type is a guess.
    searchable_data_updated_at = models.DateTimeField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)
    original_measure_sid = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    oid = models.IntegerField(blank=True, null=True)
    goods_nomenclature_item_id = models.CharField(max_length=10, blank=True, null=True)
    additional_code_id = models.CharField(max_length=3, blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'measures'


class MeursingAdditionalCodes(models.Model):
    meursing_additional_code_sid = models.IntegerField(blank=True, null=True)
    additional_code = models.CharField(max_length=3, blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)
    added_by_id = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'meursing_additional_codes'


class MeursingHeadingTexts(models.Model):
    meursing_table_plan_id = models.CharField(max_length=2, blank=True, null=True)
    meursing_heading_number = models.IntegerField(blank=True, null=True)
    row_column_code = models.IntegerField(blank=True, null=True)
    language_id = models.CharField(max_length=5, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'meursing_heading_texts'


class MeursingHeadings(models.Model):
    meursing_table_plan_id = models.CharField(max_length=2, blank=True, null=True)
    meursing_heading_number = models.TextField(blank=True, null=True)
    row_column_code = models.IntegerField(blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'meursing_headings'


class MeursingSubheadings(models.Model):
    meursing_table_plan_id = models.CharField(max_length=2, blank=True, null=True)
    meursing_heading_number = models.IntegerField(blank=True, null=True)
    row_column_code = models.IntegerField(blank=True, null=True)
    subheading_sequence_number = models.IntegerField(blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'meursing_subheadings'


class MeursingTableCellComponents(models.Model):
    meursing_additional_code_sid = models.IntegerField(blank=True, null=True)
    meursing_table_plan_id = models.CharField(max_length=2, blank=True, null=True)
    heading_number = models.IntegerField(blank=True, null=True)
    row_column_code = models.IntegerField(blank=True, null=True)
    subheading_sequence_number = models.IntegerField(blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    additional_code = models.CharField(max_length=3, blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'meursing_table_cell_components'


class MeursingTablePlans(models.Model):
    meursing_table_plan_id = models.CharField(max_length=2, blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'meursing_table_plans'


class ModificationRegulations(models.Model):
    modification_regulation_role = models.IntegerField(blank=True, null=True)
    modification_regulation_id = models.CharField(max_length=255, blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    published_date = models.DateField(blank=True, null=True)
    officialjournal_number = models.CharField(max_length=255, blank=True, null=True)
    officialjournal_page = models.IntegerField(blank=True, null=True)
    base_regulation_role = models.IntegerField(blank=True, null=True)
    base_regulation_id = models.CharField(max_length=255, blank=True, null=True)
    replacement_indicator = models.IntegerField(blank=True, null=True)
    stopped_flag = models.BooleanField(blank=True, null=True)
    information_text = models.TextField(blank=True, null=True)
    approved_flag = models.BooleanField(blank=True, null=True)
    explicit_abrogation_regulation_role = models.IntegerField(blank=True, null=True)
    explicit_abrogation_regulation_id = models.CharField(max_length=8, blank=True, null=True)
    effective_end_date = models.DateTimeField(blank=True, null=True)
    complete_abrogation_regulation_role = models.IntegerField(blank=True, null=True)
    complete_abrogation_regulation_id = models.CharField(max_length=8, blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    added_by_id = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'modification_regulations'


class MonetaryExchangePeriods(models.Model):
    monetary_exchange_period_sid = models.IntegerField(blank=True, null=True)
    parent_monetary_unit_code = models.CharField(max_length=255, blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'monetary_exchange_periods'


class MonetaryExchangeRates(models.Model):
    monetary_exchange_period_sid = models.IntegerField(blank=True, null=True)
    child_monetary_unit_code = models.CharField(max_length=255, blank=True, null=True)
    exchange_rate = models.DecimalField(max_digits=16, decimal_places=8, blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'monetary_exchange_rates'


class MonetaryUnitDescriptions(models.Model):
    monetary_unit_code = models.CharField(max_length=255, blank=True, null=True)
    language_id = models.CharField(max_length=5, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'monetary_unit_descriptions'


class MonetaryUnits(models.Model):
    monetary_unit_code = models.CharField(max_length=255, blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'monetary_units'


class NomenclatureGroupMemberships(models.Model):
    goods_nomenclature_sid = models.IntegerField(blank=True, null=True)
    goods_nomenclature_group_type = models.CharField(max_length=1, blank=True, null=True)
    goods_nomenclature_group_id = models.CharField(max_length=6, blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    goods_nomenclature_item_id = models.CharField(max_length=10, blank=True, null=True)
    productline_suffix = models.CharField(max_length=2, blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'nomenclature_group_memberships'


class ProrogationRegulationActions(models.Model):
    prorogation_regulation_role = models.IntegerField(blank=True, null=True)
    prorogation_regulation_id = models.CharField(max_length=8, blank=True, null=True)
    prorogated_regulation_role = models.IntegerField(blank=True, null=True)
    prorogated_regulation_id = models.CharField(max_length=8, blank=True, null=True)
    prorogated_date = models.DateField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'prorogation_regulation_actions'


class ProrogationRegulations(models.Model):
    prorogation_regulation_role = models.IntegerField(blank=True, null=True)
    prorogation_regulation_id = models.CharField(max_length=255, blank=True, null=True)
    published_date = models.DateField(blank=True, null=True)
    officialjournal_number = models.CharField(max_length=255, blank=True, null=True)
    officialjournal_page = models.IntegerField(blank=True, null=True)
    replacement_indicator = models.IntegerField(blank=True, null=True)
    information_text = models.TextField(blank=True, null=True)
    approved_flag = models.BooleanField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    added_by_id = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'prorogation_regulations'


class PublicationSigles(models.Model):
    oid = models.IntegerField(blank=True, null=True)
    code_type_id = models.CharField(max_length=4, blank=True, null=True)
    code = models.CharField(max_length=10, blank=True, null=True)
    publication_code = models.CharField(max_length=1, blank=True, null=True)
    publication_sigle = models.CharField(max_length=20, blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'publication_sigles'


class QuotaAssociations(models.Model):
    main_quota_definition_sid = models.IntegerField(blank=True, null=True)
    sub_quota_definition_sid = models.IntegerField(blank=True, null=True)
    relation_type = models.CharField(max_length=255, blank=True, null=True)
    coefficient = models.DecimalField(max_digits=16, decimal_places=5, blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)
    added_by_id = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'quota_associations'


class QuotaBalanceEvents(models.Model):
    quota_definition_sid = models.IntegerField(blank=True, null=True)
    occurrence_timestamp = models.DateTimeField(blank=True, null=True)
    last_import_date_in_allocation = models.DateField(blank=True, null=True)
    old_balance = models.DecimalField(max_digits=15, decimal_places=3, blank=True, null=True)
    new_balance = models.DecimalField(max_digits=15, decimal_places=3, blank=True, null=True)
    imported_amount = models.DecimalField(max_digits=15, decimal_places=3, blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'quota_balance_events'


class QuotaBlockingPeriods(models.Model):
    quota_blocking_period_sid = models.IntegerField(blank=True, null=True)
    quota_definition_sid = models.IntegerField(blank=True, null=True)
    blocking_start_date = models.DateField(blank=True, null=True)
    blocking_end_date = models.DateField(blank=True, null=True)
    blocking_period_type = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'quota_blocking_periods'


class QuotaCriticalEvents(models.Model):
    quota_definition_sid = models.IntegerField(blank=True, null=True)
    occurrence_timestamp = models.DateTimeField(blank=True, null=True)
    critical_state = models.CharField(max_length=255, blank=True, null=True)
    critical_state_change_date = models.DateField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'quota_critical_events'


class QuotaDefinitions(models.Model):
    quota_definition_sid = models.IntegerField(blank=True, null=True)
    quota_order_number_id = models.CharField(max_length=255, blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    quota_order_number_sid = models.IntegerField(blank=True, null=True)
    volume = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    initial_volume = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    measurement_unit_code = models.CharField(max_length=3, blank=True, null=True)
    maximum_precision = models.IntegerField(blank=True, null=True)
    critical_state = models.CharField(max_length=255, blank=True, null=True)
    critical_threshold = models.IntegerField(blank=True, null=True)
    monetary_unit_code = models.CharField(max_length=255, blank=True, null=True)
    measurement_unit_qualifier_code = models.CharField(max_length=1, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    added_by_id = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)
    workbasket_type_of_quota = models.TextField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'quota_definitions'


class QuotaExhaustionEvents(models.Model):
    quota_definition_sid = models.IntegerField(blank=True, null=True)
    occurrence_timestamp = models.DateTimeField(blank=True, null=True)
    exhaustion_date = models.DateField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'quota_exhaustion_events'


class QuotaOrderNumberOriginExclusions(models.Model):
    quota_order_number_origin_sid = models.IntegerField(blank=True, null=True)
    excluded_geographical_area_sid = models.IntegerField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    added_by_id = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'quota_order_number_origin_exclusions'


class QuotaOrderNumberOrigins(models.Model):
    quota_order_number_origin_sid = models.IntegerField(blank=True, null=True)
    quota_order_number_sid = models.IntegerField(blank=True, null=True)
    geographical_area_id = models.CharField(max_length=255, blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    geographical_area_sid = models.IntegerField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    added_by_id = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'quota_order_number_origins'


class QuotaOrderNumbers(models.Model):
    quota_order_number_sid = models.IntegerField(blank=True, null=True)
    quota_order_number_id = models.CharField(max_length=255, blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    added_by_id = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'quota_order_numbers'


class QuotaReopeningEvents(models.Model):
    quota_definition_sid = models.IntegerField(blank=True, null=True)
    occurrence_timestamp = models.DateTimeField(blank=True, null=True)
    reopening_date = models.DateField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'quota_reopening_events'


class QuotaSuspensionPeriods(models.Model):
    quota_suspension_period_sid = models.IntegerField(blank=True, null=True)
    quota_definition_sid = models.IntegerField(blank=True, null=True)
    suspension_start_date = models.DateField(blank=True, null=True)
    suspension_end_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)
    added_by_id = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'quota_suspension_periods'


class QuotaUnblockingEvents(models.Model):
    quota_definition_sid = models.IntegerField(blank=True, null=True)
    occurrence_timestamp = models.DateTimeField(blank=True, null=True)
    unblocking_date = models.DateField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'quota_unblocking_events'


class QuotaUnsuspensionEvents(models.Model):
    quota_definition_sid = models.IntegerField(blank=True, null=True)
    occurrence_timestamp = models.DateTimeField(blank=True, null=True)
    unsuspension_date = models.DateField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)
    added_by_id = models.IntegerField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'quota_unsuspension_events'


class RegulationGroupDescriptions(models.Model):
    regulation_group_id = models.CharField(max_length=255, blank=True, null=True)
    language_id = models.CharField(max_length=5, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'regulation_group_descriptions'


class RegulationGroups(models.Model):
    regulation_group_id = models.CharField(max_length=255, blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'regulation_groups'


class RegulationReplacements(models.Model):
    geographical_area_id = models.CharField(max_length=255, blank=True, null=True)
    chapter_heading = models.CharField(max_length=255, blank=True, null=True)
    replacing_regulation_role = models.IntegerField(blank=True, null=True)
    replacing_regulation_id = models.CharField(max_length=255, blank=True, null=True)
    replaced_regulation_role = models.IntegerField(blank=True, null=True)
    replaced_regulation_id = models.CharField(max_length=255, blank=True, null=True)
    measure_type_id = models.CharField(max_length=3, blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'regulation_replacements'


class RegulationRoleTypeDescriptions(models.Model):
    regulation_role_type_id = models.CharField(max_length=255, blank=True, null=True)
    language_id = models.CharField(max_length=5, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'regulation_role_type_descriptions'


class RegulationRoleTypes(models.Model):
    regulation_role_type_id = models.IntegerField(blank=True, null=True)
    validity_start_date = models.DateTimeField(blank=True, null=True)
    validity_end_date = models.DateTimeField(blank=True, null=True)
    national = models.BooleanField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'regulation_role_types'


class RegulationsSearchPgView(models.Model):
    id = models.TextField(primary_key=True)
    regulation_id = models.CharField(max_length=20, blank=True, null=True)
    role = models.IntegerField(blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    published_date = models.DateField(blank=True, null=True)
    officialjournal_number = models.CharField(max_length=255, blank=True, null=True)
    officialjournal_page = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    added_at = models.DateTimeField(blank=True, null=True)
    added_by_id = models.IntegerField(blank=True, null=True)
    regulation_group_id = models.CharField(max_length=20, blank=True, null=True)
    replacement_indicator = models.IntegerField(blank=True, null=True)
    keywords = models.TextField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'regulations_search_pg_view'


class TransmissionComments(models.Model):
    comment_sid = models.IntegerField(blank=True, null=True)
    language_id = models.CharField(max_length=5, blank=True, null=True)
    comment_text = models.TextField(blank=True, null=True)
    oid = models.IntegerField(blank=True, null=True)
    operation = models.CharField(max_length=1, blank=True, null=True)
    operation_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    workbasket_id = models.IntegerField(blank=True, null=True)
    workbasket_sequence_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'transmission_comments'
