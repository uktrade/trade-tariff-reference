# Import standard modules
from __future__ import with_statement

import os
from contextlib import closing
from zipfile import ZIP_DEFLATED, ZipFile


def zipdir(model_dir, temp_file):
    with closing(ZipFile(temp_file, "w", ZIP_DEFLATED)) as z:
        for root, dirs, files in os.walk(model_dir):
            # NOTE: ignore empty directories
            for fn in files:
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
    except:
        return 0


def list_to_sql(my_list):
    s = ""
    if my_list != "":
        for o in my_list:
            s += "'" + o + "', "
        s = s.strip()
        s = s.strip(",")
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
