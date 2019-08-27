import codecs
import logging
import os
import tempfile
from distutils.dir_util import copy_tree

from django.template.loader import render_to_string

from docx import Document

from docxcompose.composer import Composer

from trade_tariff_reference.documents import functions as f
from trade_tariff_reference.documents.utils import upload_generic_document_to_s3
from trade_tariff_reference.schedule.models import Chapter as DBChapter

from .commodity import Commodity
from .constants import (
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
        if self.chapter.id in [2, 9, 10, 11]:  # These all have misture rule, therefore a wider notes column
            return [600, 900, 1150, 2350]

        if self.contains_authorised_use:
            return [600, 1050, 1100, 2250]
        return [600, 1050, 600, 2750]

    def format_sibling_duties(self, commodity_count, commodity_list):
        for loop1 in range(0, commodity_count):
            sibling_duties = []
            my_commodity = commodity_list[loop1]
            if my_commodity.significant_digits == 10:
                if my_commodity.combined_duty != "":
                    sibling_duties.append(my_commodity.combined_duty)
                    if loop1 < commodity_count:
                        for loop2 in range(loop1 + 1, commodity_count):
                            next_commodity = commodity_list[loop2]
                            if next_commodity.indents == my_commodity.indents:
                                sibling_duties.append(next_commodity.combined_duty)
                            else:
                                sibling_duty_set = set(sibling_duties)
                                break

    def write(self, document_xml):
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
        try:
            self.section_numeral = row[0]
        except:
            self.section_numeral = ""
            logger.error("Chapter does not exist")
            return
        self.section_title = row[1]
        self.sSectionID = row[2]

        self.new_section = False
        for r in self.application.section_chapter_list:
            if int(r[0]) == self.chapter.id:
                self.new_section = r[2]
                break

    def get_duties(self):
        ###############################################################
        # Get the duties
        # And this is what is new
        rows = self.application.execute_sql(
            GET_DUTIES.format(chapter_string=self.chapter.chapter_string)
        )

        # Do a pass through the duties table and create a full duty expression
        duty_list = []
        for row in rows:
            commodity_code = f.mstr(row[0])
            additional_code_type_id = f.mstr(row[1])
            additional_code_id = f.mstr(row[2])
            measure_type_id = f.mstr(row[3])
            duty_expression_id = f.mstr(row[4])
            duty_amount = row[5]
            monetary_unit_code = f.mstr(row[6])
            monetary_unit_code = monetary_unit_code.replace("EUR", "€")
            measurement_unit_code = f.mstr(row[7])
            measurement_unit_qualifier_code = f.mstr(row[8])
            measure_sid = f.mstr(row[9])

            oDuty = Duty(
                commodity_code, additional_code_type_id, additional_code_id, measure_type_id, duty_expression_id,
                duty_amount, monetary_unit_code, measurement_unit_code, measurement_unit_qualifier_code, measure_sid
            )
            duty_list.append(oDuty)
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

        body_string = render_to_string(self.xml_template_name, context_dict)
        self.write(body_string)

    def format_heading(self):
        heading = {}
        if self.new_section is True:
            heading['HEADINGa'] = "Section " + self.section_numeral
            heading['HEADINGb'] = self.section_title

        heading['CHAPTER'] = "Chapter " + self.chapter.chapter_string
        heading['HEADING'] = self.chapter.description
        return heading

    def format_schedule_chapter(self, commodity_list):
        # Assign duties to those commodities as appropriate
        for my_commodity in commodity_list:
            for d in self.duty_list:
                if my_commodity.commodity_code == d.commodity_code:
                    if my_commodity.product_line_suffix == "80":
                        my_commodity.duty_list.append(d)
                        my_commodity.assigned = True

            my_commodity.combine_duties()
            my_commodity.format_commodity_code(my_commodity.commodity_code)

        ###########################################################################
        # Get exceptions
        ###########################################################################

        for my_commodity in commodity_list:
            my_commodity.check_for_specials()
            my_commodity.check_for_authorised_use()
            if my_commodity.combined_duty == "AU":
                self.contains_authorised_use = True
            self.seasonal_records += my_commodity.check_for_seasonal()

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

        for indent in range(max_indent, -1, -1):
            for loop1 in range(0, commodity_count):
                my_commodity = commodity_list[loop1]
                if my_commodity.indents == indent:
                    if my_commodity.significant_digits == 10:
                        for loop2 in range(loop1 - 1, -1, -1):
                            upper_commodity = commodity_list[loop2]
                            if upper_commodity.indents == my_commodity.indents - 1:
                                if upper_commodity.combined_duty == my_commodity.combined_duty:
                                    my_commodity.suppress_row = True
                                    break

                            if self.chapter.id in (97, 47, 80, 14, 48, 49):
                                if upper_commodity.indents <= 1 and upper_commodity.significant_digits == 2:
                                    break
                            else:
                                if upper_commodity.indents <= 1 and upper_commodity.significant_digits > 2:
                                    break
        self.format_sibling_duties(commodity_count, commodity_list)

        ###########################################################################
        # Only suppress the duty if the item is not PLS of 80
        # This will change to be - only suppress if not a leaf
        ###########################################################################

        for loop1 in range(0, commodity_count):
            my_commodity = commodity_list[loop1]
            if my_commodity.product_line_suffix != "80":
                my_commodity.suppress_duty = True
            else:
                my_commodity.suppress_duty = False

        table_content = self.format_table_content(commodity_list)
        return table_content


class ClassificationChapter(Chapter):
    document_title = "UK Goods Classification"
    xml_template_name = 'xml/mfn/document_classification.xml'
    document_file_field = 'classification_document'

    def format_chapter(self):
        commodity_list = self.get_commodity_list()
        self.format_classification_chapter(commodity_list)

    def format_classification_chapter(self, commodity_list):
        commodity_count = len(commodity_list)
        self.format_sibling_duties(commodity_count, commodity_list)

        table_content = self.format_table_content(commodity_list)
        document_content = self.get_document_content()
        context_dict = {
            **table_content,
            **document_content,
        }

        body_string = render_to_string(self.xml_template_name, context_dict)
        self.write(body_string)

    def prepend_introduction(self, filename):
        master_document = Document(self.chapter.note.document)
        composer = Composer(master_document)
        my_chapter_file = Document(filename)
        composer.append(my_chapter_file)
        composer.save(filename)
