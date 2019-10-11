import codecs
import logging
import os
import tempfile
from distutils.dir_util import copy_tree
from unicodedata import normalize

from botocore.exceptions import EndpointConnectionError

from django.template.loader import render_to_string

from docx import Document

from docxcompose.composer import Composer

from trade_tariff_reference.documents import functions as f
from trade_tariff_reference.documents.history import ChapterDocumentHistoryLog
from trade_tariff_reference.documents.utils import upload_generic_document_to_s3
from trade_tariff_reference.schedule.models import Chapter as DBChapter

from .commodity import Commodity
from .constants import (
    BUS_TYRES_COMMODITY_CODES,
    CLASSIFICATION,
    GET_CLASSIFICATIONS,
    GET_DUTIES,
    GET_SECTION_DETAILS,
    SCHEDULE,
)
from .duty import Duty


logger = logging.getLogger(__name__)


def process_chapter(application, chapter_id):
    if chapter_id in [77, 98, 99]:
        return
    chapter = get_chapter(chapter_id)
    if not chapter:
        logger.error(f'Error: No chapter found of {chapter_id}')
        return

    if application.document_type == CLASSIFICATION:
        chapter = ClassificationChapter(application, chapter)
    else:
        chapter = ScheduleChapter(application, chapter)
    chapter.format_chapter()


def get_chapter(chapter_id):
    try:
        return DBChapter.objects.get(id=chapter_id)
    except DBChapter.DoesNotExist:
        return


class Chapter:
    document_file_field = 'document'

    def __init__(self, application, chapter):
        self.application = application
        self.chapter = chapter

        self.footnote_list = []
        self.duty_list = []
        self.supplementary_unit_list = []
        self.seasonal_records = 0
        self.contains_authorised_use = False

        logger.info(f"Creating {self.application.document_type} for chapter {self.chapter.chapter_string}")

        self.get_section_details()
        self.duty_list = self.get_duties()

    def get_commodity_list(self):
        rows = self.application.execute_sql(
            GET_CLASSIFICATIONS.format(chapter_string=self.chapter.chapter_string)
        )
        commodity_list = []
        # Make a list of commodities
        for row in rows:
            commodity_code = row[0]
            productline_suffix = f.mstr(row[1])
            description = row[2]
            number_indents = f.mnum(row[3])
            leaf = 0

            my_commodity = Commodity(
                self.application, commodity_code, description, productline_suffix, number_indents, leaf
            )
            commodity_list.append(my_commodity)
        return commodity_list

    def format_table_content(self, commodity_list):
        new_list = []

        for my_commodity in commodity_list:
            commodity_dict = {}
            if my_commodity.suppress_row is False:
                if self.application.document_type == SCHEDULE:
                    my_commodity.check_for_mixture()
                    my_commodity.combine_notes()

                commodity_dict['COMMODITY'] = my_commodity.commodity_code_formatted
                description = my_commodity.description_formatted
                commodity_dict['DESCRIPTION'] = str(description)

                commodity_dict['INDENT'] = my_commodity.indent_string
                if my_commodity.suppress_duty is True:
                    commodity_dict['DUTY'] = f.surround("")
                    commodity_dict['NOTES'] = ''
                else:
                    commodity_dict['DUTY'] = f.surround(my_commodity.combined_duty)
                    commodity_dict['NOTES'] = my_commodity.notes_string
                new_list.append(commodity_dict)

        return {'commodity_list': new_list}

    def get_document_content(self):
        width_list = self.get_width_list()
        document_dict = {
            'WIDTH_CLASSIFICATION': str(width_list[0]),
            'WIDTH_DUTY': str(width_list[1]),
            'WIDTH_NOTES': str(width_list[2]),
            'WIDTH_DESCRIPTION': str(width_list[3])
        }
        return document_dict

    def get_width_list(self):
        if self.chapter.id in [2, 9, 10, 11]:  # These all have mixture rule, therefore a wider notes column
            return [600, 900, 1150, 2350]

        if self.contains_authorised_use:
            return [600, 1050, 1100, 2250]
        return [600, 1050, 600, 2750]

    def create_document(self, context):
        chapter_log = ChapterDocumentHistoryLog(
            self.chapter,
            context,
            self.application.force_document_generation,
            self.application.document_type
        )
        if chapter_log.change == dict() and not self.application.force_document_generation:
            logger.info(
                f'PROCESS COMPLETE - Document for {self.application.document_type}'
                f' {self.chapter.chapter_string} unchanged no file generated'
            )
            return

        document_xml = render_to_string(self.xml_template_name, context)
        try:
            remote_file_name = self.write(document_xml)
        except EndpointConnectionError:
            logger.error(
                f'Error - Cannot connect to S3 unable to update document for {self.chapter.chapter_string}'
            )
        else:
            chapter_log.log_document_history(remote_file_name)

    def write(self, document_xml):
        document_xml = normalize('NFKD', document_xml)
        document_xml = f.apply_value_format_to_document(document_xml)
        ###########################################################################
        # WRITE document.xml
        ###########################################################################
        model_dir = self.application.MODEL_DIR

        with tempfile.TemporaryDirectory(prefix='mfn_document_generation') as tmp_model_dir:
            copy_tree(model_dir, tmp_model_dir)

            tmp_word_dir = os.path.join(tmp_model_dir, "word")

            file_name = os.path.join(tmp_word_dir, "document.xml")
            file = codecs.open(file_name, "w", "utf-8")
            file.write(document_xml)
            file.close()

            ###########################################################################
            # Finally, ZIP everything up
            ###########################################################################
            temp_doc_file = tempfile.NamedTemporaryFile()
            f.zipdir(tmp_model_dir, temp_doc_file)
            self.prepend_introduction(temp_doc_file.name)

            remote_file_name = f'{self.application.document_type}{self.chapter.chapter_string}.docx'
            upload_generic_document_to_s3(
                self.chapter, self.document_file_field, temp_doc_file.name, remote_file_name
            )
            logger.info(f"PROCESS COMPLETE - {remote_file_name} created")
            return remote_file_name

    def prepend_introduction(self, filename):
        return

    def get_section_details(self):
        ###############################################################
        # Get the section header
        # Relevant to both the classification and the schedule
        row = self.application.execute_sql(
            GET_SECTION_DETAILS.format(chapter_string=self.chapter.chapter_string),
            only_one_row=True
        )
        if not row:
            self.section_numeral = ""
            logger.error("Chapter does not exist")
            return

        self.section_numeral = row[0]
        self.section_title = row[1]
        self.sSectionID = row[2]

        self.new_section = False
        for r in self.application.section_chapter_list:
            if int(r[0]) == self.chapter.id:
                self.new_section = r[2]
                break

    def get_duties(self):
        rows = self.application.execute_sql(
            GET_DUTIES.format(chapter_string=self.chapter.chapter_string),
            dict_cursor=True
        )

        duty_list = []

        for row in rows:
            commodity_code = f.mstr(row['goods_nomenclature_item_id'])
            additional_code_type_id = f.mstr(row['additional_code_type_id'])
            additional_code_id = f.mstr(row['additional_code_id'])
            measure_type_id = f.mstr(row['measure_type_id'])
            duty_expression_id = f.mstr(row['duty_expression_id'])
            duty_amount = row['duty_amount']
            monetary_unit_code = f.mstr(row['monetary_unit_code'])
            monetary_unit_code = monetary_unit_code.replace("EUR", "€")
            measurement_unit_code = f.mstr(row['measurement_unit_code'])
            measurement_unit_qualifier_code = f.mstr(row['measurement_unit_qualifier_code'])
            measure_sid = f.mstr(row['measure_sid'])

            duty = Duty(
                commodity_code,
                additional_code_type_id,
                additional_code_id,
                measure_type_id,
                duty_expression_id,
                duty_amount,
                monetary_unit_code,
                measurement_unit_code,
                measurement_unit_qualifier_code,
                measure_sid
            )
            duty_list.append(duty)
        return duty_list


class ScheduleChapter(Chapter):
    document_title = 'UK Goods Schedule'
    xml_template_name = 'xml/mfn/document_schedule.xml'
    document_file_field = 'schedule_document'

    def format_chapter(self):
        commodity_list = self.get_commodity_list()
        table_content = self.format_schedule_chapter(commodity_list)
        document_content = self.get_document_content()
        heading_content = self.format_heading()
        context_dict = {
            **heading_content,
            **table_content,
            **document_content,
        }
        self.create_document(context_dict)

    def format_heading(self):
        heading = {}

        if self.chapter.display_section_heading:
            heading['HEADINGa'] = "Section " + self.section_numeral
            heading['HEADINGb'] = self.section_title

        heading['CHAPTER'] = "Chapter " + self.chapter.chapter_string
        heading['HEADING'] = self.chapter.description
        return heading

    def assign_duties_to_commodities(self, commodity_list):
        # Assign duties to those commodities as appropriate
        for my_commodity in commodity_list:
            for d in self.duty_list:
                if my_commodity.commodity_code == d.commodity_code:
                    if my_commodity.product_line_suffix == "80":
                        my_commodity.duty_list.append(d)
                        my_commodity.assigned = True

            my_commodity.combine_duties()
            my_commodity.set_formatted_commodity_code(my_commodity.commodity_code)

    def assign_authorised_use_commodities(self, commodity_list):
        ###########################################################################
        # Get exceptions
        ###########################################################################
        for my_commodity in commodity_list:
            my_commodity.check_for_specials()
            my_commodity.check_for_authorised_use()
            if my_commodity.combined_duty == "AU":
                self.contains_authorised_use = True
            self.seasonal_records += my_commodity.check_for_seasonal()

    def assign_inherited_duty_to_commodity(self, commodity_list):
        #######################################################################################
        # The purpose of the code below is to loop down through all commodity codes in
        # this chapter and, for each commodity code, then loop back up through the commodity
        # code hierarchy to find any duties that could be inherited down to the current
        # commodity code, in case there is no duty explicity assigned to the commodity code.
        # This is achieved by looking for the 1st commodity code with a lower indent (to find
        # the immediate antecedent) and viewing the assigned duty.
        #
        # In case of commodities where the duties are set at CN chapter level
        # (in the EU this is chapters 97, 47, 80, 14, 48, 49), this is a special case to look out for,
        # as both the CN chapter and the CN subheading have an indent of 0, therefore number of
        # significant digits needs to be used as a comparator instead of indents
        #######################################################################################

        commodity_count = len(commodity_list)
        max_indent = -1
        for loop1 in range(0, commodity_count):
            my_commodity = commodity_list[loop1]
            yardstick_indent = my_commodity.indents

            if my_commodity.indents > max_indent:
                max_indent = my_commodity.indents

            if my_commodity.combined_duty == "":
                for loop2 in range(loop1 - 1, -1, -1):
                    upper_commodity = commodity_list[loop2]
                    if my_commodity.significant_digits == 4:
                        if upper_commodity.significant_digits == 2:
                            if upper_commodity.combined_duty != "":
                                my_commodity.combined_duty = upper_commodity.combined_duty
                            break
                    else:
                        if upper_commodity.indents < yardstick_indent:
                            if upper_commodity.combined_duty != "":
                                my_commodity.combined_duty = upper_commodity.combined_duty
                                break
                            elif upper_commodity.indents == 0:
                                break
                            yardstick_indent = upper_commodity.indents

        return max_indent

    def format_schedule_chapter(self, commodity_list):
        self.assign_duties_to_commodities(commodity_list)
        self.assign_authorised_use_commodities(commodity_list)
        max_indent = self.assign_inherited_duty_to_commodity(commodity_list)
        self.suppress_row_for_commodity(commodity_list, max_indent)
        self.unsuppress_selected_commodities(commodity_list)
        self.suppress_none_product_line(commodity_list)
        self.suppress_child_duty(commodity_list, max_indent)
        table_content = self.format_table_content(commodity_list)
        return table_content

    def suppress_row_for_commodity(self, commodity_list, max_indent):
        ###########################################################################
        # This function is intended to suppress rows where there is no reason to show them
        # We are only going to suppress rows where the goods is of 10 significant digits
        # (i.e.) it does not end with "00" and where there is no difference in the
        # applicable duty for it and all its siblings
        #
        # The first way to look at this is to find all codes with 10 significant digits
        # and suppress them when they have the same duty as their parent (by indent).
        # This is only going to work where the duty has been set at a higher level and
        # inherited down - it will not work where the duty has been actually set at
        # 10-digit level and should be inherited up
        ###########################################################################
        commodity_count = len(commodity_list)
        for indent in range(max_indent, -1, -1):
            for loop1 in range(0, commodity_count):
                my_commodity = commodity_list[loop1]
                if my_commodity.indents == indent:
                    if my_commodity.significant_digits == 10:
                        if my_commodity.assigned is True:
                            my_commodity.prevent_row_suppression = True
                            my_commodity.suppress_row = False

                        if my_commodity.prevent_row_suppression is False:
                            for loop2 in range(loop1 - 1, -1, -1):
                                upper_commodity = commodity_list[loop2]
                                sibling_duty_list = []
                                if upper_commodity.indents == my_commodity.indents - 1:
                                    for loop3 in range(loop2 + 1, commodity_count):
                                        sibling_commodity = commodity_list[loop3]
                                        if sibling_commodity.indents >= my_commodity.indents:
                                            sibling_duty_list.append(sibling_commodity.combined_duty)
                                        elif sibling_commodity.indents < my_commodity.indents:
                                            break

                                    for i in range(len(sibling_duty_list) - 1, -1, -1):
                                        item = sibling_duty_list[i]
                                        if item == "":
                                            del sibling_duty_list[i]

                                    sibling_duty_set = set(sibling_duty_list)
                                    if len(sibling_duty_set) > 1:
                                        my_commodity.suppress_row = False
                                        #  Start new bit
                                        if "AU" in sibling_duty_set:
                                            for loop3 in range(loop2 + 1, commodity_count):
                                                child = commodity_list[loop3]
                                                if child.indents > my_commodity.indents:
                                                    child.prevent_row_suppression = True
                                                else:
                                                    break
                                    # End new bit
                                    else:
                                        if my_commodity.prevent_row_suppression is False:
                                            my_commodity.suppress_row = True
                                    break

                                # if upper_commodity.indents <= 1 and upper_commodity.significant_digits > 2:
                                if upper_commodity.significant_digits == 2:
                                    break

    def unsuppress_selected_commodities(self, commodity_list):
        for comm in commodity_list:
            if comm.commodity_code in BUS_TYRES_COMMODITY_CODES:
                comm.suppress_row = False
                comm.suppress_duty = False

    def suppress_none_product_line(self, commodity_list):
        ###########################################################################
        # Suppress the duty if the item is not PLS of 80
        # This will change to be - only supppress if not a leaf
        ###########################################################################
        for commodity in commodity_list:
            if commodity.product_line_suffix != "80":
                commodity.suppress_duty = True
            else:
                commodity.suppress_duty = False

    def suppress_child_duty(self, commodity_list, max_indent):
        ###########################################################################
        # Also suppress the duty if the item has children that are displayed
        ###########################################################################
        commodity_count = len(commodity_list)
        for loop in range(max_indent, -1, -1):
            for loop1 in range(0, commodity_count):
                my_commodity = commodity_list[loop1]
                if my_commodity.indents == loop:
                    my_commodity.has_children = False
                    for loop2 in range(loop1 + 1, commodity_count):
                        child_commodity = commodity_list[loop2]
                        if child_commodity.indents <= my_commodity.indents:
                            break
                        else:
                            if child_commodity.suppress_row is False:
                                my_commodity.has_children = True
                                break

                    if my_commodity.has_children:
                        my_commodity.suppress_duty = True


class ClassificationChapter(Chapter):
    document_title = "UK Goods Classification"
    xml_template_name = 'xml/mfn/document_classification.xml'
    document_file_field = 'classification_document'

    def format_chapter(self):
        commodity_list = self.get_commodity_list()
        self.format_classification_chapter(commodity_list)

    def format_classification_chapter(self, commodity_list):
        table_content = self.format_table_content(commodity_list)
        document_content = self.get_document_content()
        chapter_note_content = self.get_chapter_note_content()
        context_dict = {
            **table_content,
            **document_content,
            **chapter_note_content,
        }
        self.create_document(context_dict)

    def prepend_introduction(self, filename):
        master_document = Document(self.chapter.note.document)
        composer = Composer(master_document)
        my_chapter_file = Document(filename)
        composer.append(my_chapter_file)
        composer.save(filename)

    def get_chapter_note_content(self):
        check_sum = ''
        chapter_note = getattr(self.chapter, 'note', None)
        if chapter_note:
            check_sum = self.chapter.note.document_check_sum
        return {
            'CHAPTER_NOTE_DOCUMENT': check_sum
        }
