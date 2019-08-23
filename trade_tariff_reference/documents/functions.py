# Import standard modules
from __future__ import with_statement

import os
import re
from contextlib import closing
from zipfile import ZIP_DEFLATED, ZipFile


def zipdir(model_dir, temp_file):
    with closing(ZipFile(temp_file, "w", ZIP_DEFLATED)) as z:
        for root, dirs, files in os.walk(model_dir):
            # NOTE: ignore empty directories
            for fn in files:
                if fn != ".DS_Store":
                    absfn = os.path.join(root, fn)
                    zfn = absfn[len(model_dir) + len(os.sep):]  # XXX: relative path
                    z.write(absfn, zfn)


def mstr(x):
    if x is None:
        return ""
    else:
        return str(x)


def mnum(x):
    try:
        if x is None:
            return 0
        else:
            return int(x)
    except ValueError:
        return 0


def list_to_sql(my_list):
    if not my_list:
        return ''
    items = [f"'{o}'" for o in my_list]
    s = ', '.join(items)
    return s


def get_measurement_unit(abbreviation):
    units_dict = {
        'ASV': '% vol',
        'NAR': 'item',
        'CCT': 'ct/l',
        'CEN': '100 p/st',
        'CTM': 'c/k',
        'DTN': '100 kg',
        'GFI': 'gi F/S',
        'GRM': 'g',
        'HLT': 'hl',
        'HMT': '100 m',
        'KGM': 'kg',
        'KLT': '1,000 l',
        'KMA': 'kg met.am.',
        'KNI': 'kg N',
        'KNS': 'kg H202',
        'KPH': 'kg KOH',
        'KPO': 'kg K20',
        'KPP': 'kg P205',
        'KSD': 'kg 90 % sdt',
        'KSH': 'kg NaOH',
        'KUR': 'kg U',
        'LPA': 'l alc. 100%',  # "l (expressed in equivalent of pure alcohol)"
        'LTR': 'l',
        'MIL': '1,000 items',
        'MTK': 'm2',
        'MTQ': 'm3',
        'MTR': 'm',
        'MWH': '1,000 kWh',
        'NCL': 'ce/el',
        'NPR': 'pa',
        'TJO': 'TJ',
        'TNE': 'tonne',
    }
    return units_dict.get(abbreviation, abbreviation)


def get_measurement_unit_qualifier_code(qualifier_code):
    unit_dict = {
        'A': 'tot alc',
        'C': '1 000',
        'E': 'net drained wt',
        'G': 'gross',
        'M': 'net dry',
        'P': 'lactic matter',
        'R': 'std qual',
        'S': 'raw sugar',
        'T': 'dry lactic matter',
        'X': 'hl',
        'Z': '% sacchar'
    }
    return unit_dict.get(qualifier_code, '')


def surround(xml):
    if not xml:
        xml = ''
    if "<w:t>" in xml:
        return xml
    return f"<w:r><w:t>{xml}</w:t></w:r>"


def format_seasonal_expression(s):
    s = mstr(s)
    s = s.replace("EUR", "€")
    s = s.replace("DTN G", "/ 100 kg gross")
    s = s.replace("DTN", "/ 100 kg")
    return s


def remove_header_footer_xml(xml):
    response = ""
    position_1 = xml.find("<w:body")
    position_2 = xml.find("<w:sectPr")
    if position_1 > 0 and position_2 > 0:
        response = xml[position_1 + 8: position_2]
    return response


def apply_value_format_to_document(document_xml_string):
    document_xml_string = re.sub(
        " ([0-9]{1,4}),([0-9]{1,4}) ", " \\1.\\2 ", document_xml_string, flags=re.MULTILINE
    )
    document_xml_string = re.sub(
        "([0-9]{1,4}),([0-9]{1,4})/", "\\1.\\2/", document_xml_string, flags=re.MULTILINE
    )
    document_xml_string = re.sub(
        " ([0-9]{1,4}),([0-9]{1,4})%", " \\1.\\2%", document_xml_string, flags=re.MULTILINE
    )
    document_xml_string = re.sub(
        " ([0-9]{1,4}),([0-9]{1,4})\\)", " \\1.\\2)", document_xml_string, flags=re.MULTILINE
    )
    document_xml_string = re.sub("([0-9]),([0-9])%", "\\1.\\2%", document_xml_string, flags=re.MULTILINE)
    document_xml_string = re.sub("([0-9]),([0-9]) kg", "\\1.\\2 kg", document_xml_string, flags=re.MULTILINE)
    document_xml_string = re.sub("([0-9]),([0-9]) Kg", "\\1.\\2 kg", document_xml_string, flags=re.MULTILINE)
    document_xml_string = re.sub("([0-9]),([0-9])kg", "\\1.\\2kg", document_xml_string, flags=re.MULTILINE)
    document_xml_string = re.sub("([0-9]),([0-9])Kg", "\\1.\\2kg", document_xml_string, flags=re.MULTILINE)
    document_xml_string = re.sub("([0-9]),([0-9]{1,3}) g", "\\1.\\2 g", document_xml_string, flags=re.MULTILINE)
    document_xml_string = re.sub("([0-9]),([0-9]{1,3})g", "\\1.\\2g", document_xml_string, flags=re.MULTILINE)
    document_xml_string = re.sub("([0-9]),([0-9]{1,3}) m", "\\1.\\2 m", document_xml_string, flags=re.MULTILINE)
    document_xml_string = re.sub("([0-9]),([0-9]{1,3})m", "\\1.\\2m", document_xml_string, flags=re.MULTILINE)

    document_xml_string = re.sub("([0-9]),([0-9]) C", "\\1.\\2 C", document_xml_string, flags=re.MULTILINE)

    document_xml_string = re.sub("([0-9]),([0-9]{1,3}) dl", "\\1.\\2 dl", document_xml_string, flags=re.MULTILINE)

    document_xml_string = re.sub(
        "([0-9]),([0-9]{1,3}) decitex", "\\1.\\2 decitex", document_xml_string, flags=re.MULTILINE
    )
    document_xml_string = re.sub("([0-9]),([0-9]{1,3}) l", "\\1.\\2 l", document_xml_string, flags=re.MULTILINE)
    document_xml_string = re.sub("([0-9]),([0-9]{1,3}) kW", "\\1.\\2 kW", document_xml_string, flags=re.MULTILINE)
    document_xml_string = re.sub("([0-9]),([0-9]{1,3}) W", "\\1.\\2 W", document_xml_string, flags=re.MULTILINE)
    document_xml_string = re.sub("([0-9]),([0-9]{1,3}) V", "\\1.\\2 V", document_xml_string, flags=re.MULTILINE)
    document_xml_string = re.sub("([0-9]),([0-9]{1,3}) Ah", "\\1.\\2 Ah", document_xml_string, flags=re.MULTILINE)
    document_xml_string = re.sub("([0-9]),([0-9]{1,3}) bar", "\\1.\\2 bar", document_xml_string, flags=re.MULTILINE)
    document_xml_string = re.sub("([0-9]),([0-9]{1,3}) cm", "\\1.\\2 cm", document_xml_string, flags=re.MULTILINE)
    document_xml_string = re.sub("([0-9]),([0-9]{1,3}) Nm", "\\1.\\2 Nm", document_xml_string, flags=re.MULTILINE)
    document_xml_string = re.sub("([0-9]),([0-9]{1,3}) kV", "\\1.\\2 kV", document_xml_string, flags=re.MULTILINE)
    document_xml_string = re.sub("([0-9]),([0-9]{1,3}) kHz", "\\1.\\2 kHz", document_xml_string, flags=re.MULTILINE)
    document_xml_string = re.sub("([0-9]),([0-9]{1,3}) kV", "\\1.\\2 kV", document_xml_string, flags=re.MULTILINE)
    document_xml_string = re.sub("([0-9]),([0-9]{1,3}) MHz", "\\1.\\2 MHz", document_xml_string, flags=re.MULTILINE)
    document_xml_string = re.sub("([0-9]),([0-9]{1,3}) μm", "\\1.\\2 μm", document_xml_string, flags=re.MULTILINE)
    document_xml_string = re.sub("([0-9]),([0-9]{1,3}) Ohm", "\\1.\\2 Ohm", document_xml_string, flags=re.MULTILINE)
    document_xml_string = re.sub("([0-9]),([0-9]{1,3}) dB", "\\1.\\2 dB", document_xml_string, flags=re.MULTILINE)
    document_xml_string = re.sub(
        "([0-9]),([0-9]{1,3}) kvar", "\\1.\\2 kvar", document_xml_string, flags=re.MULTILINE
    )
    document_xml_string = re.sub("±([0-9]),([0-9]{1,3})", "±\\1.\\2", document_xml_string, flags=re.MULTILINE)
    document_xml_string = re.sub(
        "€ ([0-9]{1,3}),([0-9]{1,3})", "€ \\1.\\2", document_xml_string, flags=re.MULTILINE
    )
    return document_xml_string
