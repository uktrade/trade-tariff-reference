# Import standard modules
from __future__ import with_statement
from contextlib import closing
from zipfile import ZipFile, ZIP_DEFLATED
from datetime import datetime
import os
import re

import glob as g

def formatFootnote(s):
    sOut = ""
    a = s.split("\n")
    for ax in a:
        ax.strip()
        #print (ax)
        if len(ax) > 0:
            lChar = ascii(ax[0])
            lChar = ord(ax[0])
            if lChar == 8226:
                sStyle = "ListBulletinTable"
            else:
                sStyle = "NormalinTable"
            ax = ax.replace(chr(8226) + "\t", "")
            ax = ax.replace("  ", " ")
            sOut += "<w:p><w:pPr><w:pStyle w:val=\"" + sStyle + "\"/></w:pPr><w:r><w:t>" + ax + "</w:t></w:r></w:p>"
    return (sOut)

def fmtMeasureTypeDescription(s):
    s = s.replace("end-use", "authorised use")
    return s

def fmtDate(d):
    try:
        d = datetime.strftime(d, '%d-%m-%y')
    except:
        d = ""
    return d

def fmtMarkdown(s):
    s = re.sub("<table.*</table>", "", s, flags=re.DOTALL)
    s = re.sub("<sup>", "", s, flags=re.DOTALL)
    s = re.sub("</sup>", "", s, flags=re.DOTALL)
    s = re.sub("_", "\"", s, flags=re.DOTALL)
    s = s.replace("  ", " ")
    sOut = ""
    a = s.split("\n")
    for ax in a:
        if ax[:2] == "##":
            sTemp = app.sHeading3XML
            sTemp = sTemp.replace("{HEADING}", ax.strip())
            sTemp = sTemp.replace("\.", ".")
            sTemp = sTemp.replace("##", "")
            sOut += sTemp
        elif ax[:4] == "  * ":
            sTemp = ax.strip()
            sTemp = sTemp.replace("* -", "")
            sTemp = sTemp.replace("* ", "")
            sTemp = sTemp.replace("\.", ".")
            sTemp = re.sub("^\([a-z]\) ", "", sTemp)
            sTemp = app.sBulletXML.replace("{TEXT}", sTemp)
            sOut += sTemp
        elif ax[:2] == "* ":
            sTemp = app.sParaXML
            sTemp = sTemp.replace("{TEXT}", ax.strip())
            sTemp = sTemp.replace("* ", "")
            sTemp = sTemp.replace("\.", ".")
            sOut += sTemp
        elif ax[:1] == "*":
            sTemp = app.sParaXML
            sTemp = sTemp.replace("{TEXT}", ax.strip())
            sTemp = sTemp.replace("*", "")
            sTemp = sTemp.replace("\.", ".")
            sOut += sTemp
        else:
            sTemp = app.sParaXML
            sTemp = sTemp.replace("{TEXT}", ax.strip())
            sTemp = sTemp.replace("* ", "")
            sTemp = sTemp.replace("\.", ".")
            if sTemp != "\n":
                sOut += sTemp

    return (sOut)

def zipdir(archivename):
    BASE_DIR     = os.path.dirname(os.path.realpath(__file__))
    MODEL_DIR = os.path.join(BASE_DIR, "model")
    with closing(ZipFile(archivename, "w", ZIP_DEFLATED)) as z:
        for root, dirs, files in os.walk(MODEL_DIR):
            #NOTE: ignore empty directories
            for fn in files:
                absfn = os.path.join(root, fn)
                zfn = absfn[len(MODEL_DIR)+len(os.sep):] #XXX: relative path
                z.write(absfn, zfn)

def mstr(x):
    try:
        if x is None:
            return ""
        else:
            return str(x)
    except:
        return ""

def mnum(x):
    try:
        if x is None:
            return 0
        else:
            return int(x)
    except:
        return 0

def debug(x):
    if g.app.debug:
        print (x)

def surround(x):
    if "<w:t>" in x:
        return x
    else:
        return "<w:r><w:t>" + x + "</w:t></w:r>"

def fmtSeasonal(s):
    s = mstr(s)
    s = s.replace("EUR", "€")
    s = s.replace("DTN G", "/ 100 kg gross")
    s = s.replace("DTN", "/ 100 kg")
    return s

def list_to_sql(my_list):
    s = ""
    if my_list != "":
        for o in my_list:
            s += "'" + o + "', "
        s = s.strip()
        s = s.strip(",")
    return (s)

def getMeasurementUnit(s):
    if s == "ASV":
        return "% vol/hl" # 3302101000
    if s == "NAR":
        return "p/st"
    elif s == "CCT":
        return "ct/l"
    elif s == "CEN":
        return "100 p/st"
    elif s == "CTM":
        return "c/k"
    elif s == "DTN":
        return "100 kg"
    elif s == "GFI":
        return "gi F/S"
    elif s == "GRM":
        return "g"
    elif s == "HLT":
        return "hl" # 2209009100
    elif s == "HMT":
        return "100 m" # 3706909900
    elif s == "KGM":
        return "kg"
    elif s == "KLT":
        return "1,000 l"
    elif s == "KMA":
        return "kg met.am."
    elif s == "KNI":
        return "kg N"
    elif s == "KNS":
        return "kg H2O2"
    elif s == "KPH":
        return "kg KOH"
    elif s == "KPO":
        return "kg K2O"
    elif s == "KPP":
        return "kg P2O5"
    elif s == "KSD":
        return "kg 90 % sdt"
    elif s == "KSH":
        return "kg NaOH"
    elif s == "KUR":
        return "kg U"
    elif s == "LPA":
        #return "l alc. 100%"
        return "l (expressed in equivalent of pure alcohol)"
    elif s == "LTR":
        return "l"
    elif s == "MIL":
        return "1,000 p/st"
    elif s == "MTK":
        return "m2"
    elif s == "MTQ":
        return "m3"
    elif s == "MTR":
        return "m"
    elif s == "MWH":
        return "1,000 kWh"
    elif s == "NCL":
        return "ce/el"
    elif s == "NPR":
        return "pa"
    elif s == "TJO":
        return "TJ"
    elif s == "TNE":
        return "t" # 1005900020
        # return "1000 kg" # 1005900020
    else:
        return s