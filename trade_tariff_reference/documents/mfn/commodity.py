import logging
import re

from trade_tariff_reference.schedule.models import SeasonalQuota


logger = logging.getLogger(__name__)


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
        if len(self.notes_list) > 1:
            # print ("More than one note", self.commodity_code)
            # sys.exit()
            pass
        self.notes_list.sort(reverse=True)
        if len(self.notes_list) == 0:
            self.notes_string = "<w:r><w:t></w:t></w:r>"
        else:
            # print ("combine notes")
            self.notes_string = ""
            i = 1
            break_string = "<w:br/>"
            for n in self.notes_list:
                if i > 1:
                    break_string = "<w:br/>"
                else:
                    break_string = ""
                self.notes_string += "<w:r>" + break_string + "<w:t>" + n + "</w:t></w:r>"
                # print (n)
                i = i + 1

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
        # Italicise any Latin text based on the content of the file latin_phrases.txt
        my_phrases = []
        for latin_phrase in self.application.latin_phrases:
            latin_phrase_parts = latin_phrase.split(" ")
            if description.find(latin_phrase) > -1:
                if latin_phrase not in my_phrases:
                    description = description.replace(
                        latin_phrase, (
                            "</w:t></w:r><w:r><w:rPr><w:i/><w:iCs/></w:rPr><w:t>" + latin_phrase +
                            " </w:t></w:r><w:r><w:t xml:space='preserve'>"
                        )
                    )
                for part in latin_phrase_parts:
                    my_phrases.append(part)
                    if "thynnus" in latin_phrase:
                        my_phrases.append("thynnus")
        return description

    def format_description(self, description):
        description = self.latinise(description)
        description = str(description)

        description = description.replace("<br> ", "<br>")
        description = description.replace("|of the CN", "")
        description = description.replace("liters", "litres")
        description = description.replace("|%|", "% ")
        description = description.replace("|gram", " gram")
        description = description.replace("|g", "g")
        description = description.replace("|kg", "kg")
        description = description.replace("|", " ")
        description = re.sub("([0-9]) %", "\\1%", description)
        description = description.replace("!x!", "x")
        description = description.replace(" kg", "kg")
        description = description.replace(" -goods", " - goods")
        description = description.replace(" - ", "</w:t></w:r><w:r><w:br/><w:t xml:space='preserve'>- ")
        description = description.replace(" • ", "</w:t></w:r><w:r><w:br/><w:t xml:space='preserve'>- ")
        description = re.sub(
            r"\$(.)",
            r'</w:t></w:r><w:r><w:rPr><w:vertAlign w:val="superscript"/>'
            r'</w:rPr><w:t>\1</w:t></w:r><w:r><w:t xml:space="preserve">',
            description
        )

        if description[-3:] == "!1!":
            description = description[:-3]
        description = description.replace("\r\r", "\r")
        description = description.replace("\r\n", "\n")
        description = description.replace("\n\r", "\n")
        description = description.replace("\n\n", "\n")
        description = description.replace("\r", "\n")
        description = description.replace("<br>", "\n")
        description = description.replace("\n", "</w:t></w:r><w:r><w:br/></w:r><w:r><w:t>")
        description = description.replace("!1!", "</w:t></w:r><w:r><w:br/></w:r><w:r><w:t>")
        description = description.replace("  ", " ")
        description = description.replace("!o!", chr(176))
        description = description.replace("\xA0", " ")
        description = description.replace(" %", "%")
        description = (
                               "<w:t>-</w:t><w:tab/>" * self.indents
                           ) + "<w:t xml:space='preserve'>" + description + "</w:t>"

        # Superscripts
        description = re.sub(
            "<w:t>(.*)m2</w:t>",
            r"<w:t>\g<1>m</w:t></w:r><w:r><w:rPr><w:vertAlign w:val=\"superscript\"/></w:rPr><w:t>2</w:t>",
            description,
            flags=re.MULTILINE
        )
        description = re.sub(
            "<w:t>(.*)m3</w:t>",
            r"<w:t xml:space='preserve'>\g<1>m</w:t></w:r><w:r><w:rPr>"
            "<w:vertAlign w:val=\"superscript\"/></w:rPr><w:t>3</w:t>",
            description,
            flags=re.MULTILINE
        )
        description = re.sub(
            "<w:t>(.*)K2O</w:t>",
            r"<w:t>\g<1>K</w:t></w:r><w:r><w:rPr>"
            "<w:vertAlign w:val=\"subscript\"/></w:rPr><w:t>2</w:t></w:r><w:r><w:t>O</w:t>",
            description,
            flags=re.MULTILINE
        )
        description = re.sub(
            "<w:t>(.*)H2O2</w:t>",
            r"<w:t>\g<1>H</w:t></w:r><w:r><w:rPr><w:vertAlign w:val=\"subscript\"/>"
            "</w:rPr><w:t>2</w:t></w:r><w:r><w:t>O</w:t></w:r><w:r><w:rPr>"
            "<w:vertAlign w:val=\"subscript\"/></w:rPr><w:t>2</w:t>",
            description,
            flags=re.MULTILINE
        )
        description = re.sub(
            "<w:t>(.*)P2O5</w:t>",
            r"<w:t>\g<1>P</w:t></w:r><w:r><w:rPr><w:vertAlign w:val=\"subscript\"/></w:rPr>"
            "<w:t>2</w:t></w:r><w:r><w:t>O</w:t></w:r>"
            "<w:r><w:rPr><w:vertAlign w:val=\"subscript\"/></w:rPr><w:t>5</w:t>",
            description,
            flags=re.MULTILINE
        )

        # Subscripts
        description = re.sub(
            "@(.)",
            '</w:t></w:r><w:r><w:rPr><w:vertAlign w:val="subscript"/>'
            '</w:rPr><w:t xml:space="preserve">\\1</w:t></w:r><w:r><w:t xml:space="preserve">',
            description,
            flags=re.MULTILINE
        )

        if self.indents < 2:  # Make it bold
            description = "<w:rPr><w:b/></w:rPr>" + description
            description = description.replace(
                "<w:r><w:rPr><w:i/><w:iCs/></w:rPr>",
                "<w:r><w:rPr><w:i/><w:b/><w:iCs/></w:rPr>"
            )
            description = description.replace("<w:r>", "<w:r><w:rPr><w:b/></w:rPr>")
        description = description.replace(
            " </w:t></w:r><w:r><w:t xml:space='preserve'>,",
            "</w:t></w:r><w:r><w:t xml:space='preserve'>,"
        )
        description = description.replace("€ ", "€")

        description = description.replace(
            "<w:r><w:br/></w:r><w:r><w:t> </w:t></w:r><w:r><w:br/></w:r>",
            "<w:r><w:br/></w:r><w:r><w:t> </w:t></w:r>"
        )

        # TODO: Not all subscripts and superscripts are handled correctly removed for now
        description = description.replace('<sup>1</sup>', '')
        description = description.replace('<sup>2</sup>', '')
        description = description.replace('<sup>3</sup>', '')
        description = description.replace('<sup>4</sup>', '')
        description = description.replace('<sup>5</sup>', '')
        description = description.replace('<sup>6</sup>', '')
        description = description.replace('<sub>1</sub>', '')
        description = description.replace('<sub>2</sub>', '')
        description = description.replace('<sub>3</sub>', '')
        description = description.replace('<sub>4</sub>', '')
        description = description.replace('<sub>5</sub>', '')
        description = description.replace('<sub>6</sub>', '')
        description = description.replace('<br>', '')

        return description

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
                    if len(self.notes_list) != 0:
                        print(self.notes_list)
                    self.notes_list.append(
                        "Code reserved for authorised use; the duty rate is specified under"
                        " regulations made under section 19 of the Taxation (Cross-border Trade) Act 2018"
                    )
                    self.combined_duty = "AU"
                    self.assigned = True
                    self.special_list.append("authoriseduse")

    def check_for_seasonal(self):
        # print ("Checking for seasonal commodities")
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
