import logging

import markdown

from trade_tariff_reference.documents.mfn.description import update_description
from trade_tariff_reference.schedule.models import SeasonalQuota

logger = logging.getLogger(__name__)

AUTHORISED_USE_NOTE = (
    'Code reserved for authorised use; the duty rate is specified under regulations made under '
    'section 19 of the Taxation (Cross-border Trade) Act 2018'
)


class Commodity:

    def __init__(self, application, commodity_code="", description="", product_line_suffix="", indents=0, leaf=0):
        # Get parameters from instantiator
        self.application = application
        self.product_line_suffix = product_line_suffix
        self.commodity_code = commodity_code
        self.commodity_code_formatted = self.format_commodity_code(self.commodity_code)
        self.indents = indents
        self.leaf = leaf
        self.assigned = False
        self.combined_duty = ""
        self.notes_list = []
        self.notes_string = ""
        self.duty_list = []
        self.suppress_row = False
        self.suppress_duty = False
        self.indent_string = ""
        self.significant_children = False
        self.measure_count = 0
        self.measure_type_count = 0
        self.description = description
        self.description_formatted = self.format_description(description)
        self.significant_digits = self.get_significant_digits()
        self.indent_string = self.get_indent_string()
        self.child_duty_list = []

        self.special_list = []

    def combine_notes(self):
        self.notes_list.sort(reverse=True)
        if len(self.notes_list) == 0:
            notes_string = "<w:r><w:t></w:t></w:r>"
        else:
            notes_string = ''
            for num, n in enumerate(self.notes_list):
                br = '<w:br/>'
                if num == 0:
                    br = ''
                note = f"<w:r>{br}<w:t>{n}</w:t></w:r>"
                notes_string += note
        self.notes_string = notes_string

    def combine_duties(self):
        self.combined_duty = ""

        self.measure_list = []
        self.measure_type_list = []
        self.additional_code_list = []

        for d in self.duty_list:
            self.measure_type_list.append(d.measure_type_id)
            self.measure_list.append(d.measure_sid)
            self.additional_code_list.append(d.additional_code_id)

        measure_type_list_unique = set(self.measure_type_list)
        measure_list_unique = set(self.measure_list)
        additional_code_list_unique = set(self.additional_code_list)

        self.measure_count = len(measure_list_unique)
        self.measure_type_count = len(measure_type_list_unique)
        self.additional_code_count = len(additional_code_list_unique)

        if self.measure_count == 1 and self.measure_type_count == 1 and self.additional_code_count == 1:
            for d in self.duty_list:
                self.combined_duty += d.duty_string + " "
        else:
            if self.measure_type_count > 1:
                # self.combined_duty = "More than one measure type"
                if "105" in measure_type_list_unique:
                    for d in self.duty_list:
                        if d.measure_type_id == "105":
                            self.combined_duty += d.duty_string + " "
            elif self.additional_code_count > 1:
                # self.combined_duty = "More than one additional code"
                if "500" in additional_code_list_unique:
                    for d in self.duty_list:
                        if d.additional_code_id == "500":
                            self.combined_duty += d.duty_string + " "
                if "550" in additional_code_list_unique:
                    for d in self.duty_list:
                        if d.additional_code_id == "550":
                            self.combined_duty += d.duty_string + " "

        self.combined_duty = self.combined_duty.replace("  ", " ")
        self.combined_duty = self.combined_duty.strip()

    def latinise(self, description):
        found_latin_phrases = []

        for latin_phrase in self.application.latin_phrases:
            if description.find(latin_phrase) > -1:
                found_latin_phrases.append(latin_phrase)

        found_latin_phrases.sort(reverse=True)

        for index, phrase in enumerate(found_latin_phrases):
            description = description.replace(phrase, self.get_temp_replacement_string(index))

        for index, phrase in enumerate(found_latin_phrases):
            replacement_string = self.style_latin(phrase)
            description = description.replace(self.get_temp_replacement_string(index), replacement_string)
        return description

    def get_temp_replacement_string(self, index):
        return f'__FOUND_{index}__'

    def style_latin(self, phrase):
        return f'<i>{phrase}</i>'

    def style_bold(self, description):
        if self.indents == 0:
            return f'<b>{description}</b>'
        return description

    def replace_characters_in_description(self, description):
        replacement_list = [
            ('<br> <br><br><br>', '<br><br><br>'),
            ('•', '-'),
            ('<br><br>-', '\n\n -'),
            ('<br> <br>', ''),
            ('<br><br>', ''),
            ('|', ''),
        ]
        for find_string, replacement_string in replacement_list:
            description = description.replace(find_string, replacement_string)
        description = description.strip()
        return description

    def format_description(self, org_description):
        description = self.style_bold(org_description)
        description = self.latinise(description)
        description = self.replace_characters_in_description(description)
        html = markdown.markdown(description)
        result = update_description(html)
        return '<w:pPr><w:jc w:val="left"/></w:pPr><w:t>-</w:t><w:tab/>' * self.indents + result

    def get_significant_digits(self):
        if self.commodity_code[-8:] == '00000000':
            return 2
        elif self.commodity_code[-6:] == '000000':
            return 4
        elif self.commodity_code[-4:] == '0000':
            return 6
        elif self.commodity_code[-2:] == '00':
            return 8
        return 10

    def get_indent_string(self):
        indent_list = [0, 113, 227, 340, 454, 567, 680, 794, 907, 1020, 1134, 1247, 1361]
        try:
            indents = indent_list[self.indents]
        except IndexError:
            indents = 0

        return f'<w:ind w:left="{indents}" w:hanging="{indents}"/>'

    def format_commodity_code(self, commodity_code):
        s = commodity_code
        if self.product_line_suffix != "80":
            return ""
        if s[4:10] == "000000":
            return s[0:4]
        elif s[6:10] == "0000":
            return s[0:4] + ' ' + s[4:6]
        elif s[8:10] == "00":
            return s[0:4] + ' ' + s[4:6] + ' ' + s[6:8]
        else:
            return s[0:4] + ' ' + s[4:6] + ' ' + s[6:8] + ' ' + s[8:10]

    # self.commodity_code_formatted = self.commodity_code + ":" + str(self.indents)

    def check_for_mixture(self):
        # print ("Checking for Mixture")
        my_chapter = self.commodity_code[0:2]
        my_subheading = self.commodity_code[0:4]
        right_chars = self.commodity_code[-2:]
        if (
            my_chapter in ('02', '10', '11') or
            my_subheading in ('0904', '0905', '0906', '0907', '0908', '0909', '0910')
        ) and right_chars == "00":
            if self.combined_duty == "":
                pass
            else:
                if self.combined_duty == "AU":
                    self.notes_list.append("Mixture rule; non-mixture")
                    self.combined_duty = "<w:r><w:t>Formula</w:t></w:r><w:r><w:br/><w:t>AU</w:t></w:r>"
                else:
                    self.notes_list.append("Mixture rule; non-mixture: " + self.combined_duty)
                    self.combined_duty = "Formula"
                self.assigned = True
                self.special_list.append("mixture")

    def check_for_specials(self):
        # print ("Checking for specials")
        if len(self.application.special_list) > 0:
            for n in self.application.special_list:
                if n.commodity_code == self.commodity_code:
                    self.notes_list.append(n.note)
                    self.assigned = True
                    self.special_list.append("special")
            # print ("Adding a special on", self.commodity_code)

    def check_for_authorised_use(self):
        if self.commodity_code in self.application.authorised_use_list:
            if self.product_line_suffix == "80":
                if len(self.special_list) == 0:
                    self.notes_list.append(AUTHORISED_USE_NOTE)
                    self.combined_duty = "AU"
                    self.assigned = True
                    self.special_list.append("authoriseduse")

    def check_for_seasonal(self):
        seasonal_records = 0
        if self.product_line_suffix != "80":
            return seasonal_records

        self.combined_duty = ''
        seasonal_quotas = SeasonalQuota.objects.filter(quota_order_number_id=self.commodity_code)
        for s in seasonal_quotas:
            duty_list = []
            for season in s.seasons.all():
                xml = (
                    f"<w:r><w:t>{season.start_date} to {season.end_date}</w:t></w:r><w:r>"
                    f"<w:tab/><w:t>{season.formatted_duty}</w:t></w:r>"
                )
                duty_list.append(xml)
            self.combined_duty += '<w:r><w:br/></w:r>'.join(duty_list)
            self.notes_list.append("Seasonally variable rate")
            self.assigned = True
            self.special_list.append("seasonal")
            logging.debug("Found a seasonal")

        return seasonal_quotas.count()
