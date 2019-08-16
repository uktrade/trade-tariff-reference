import functions as f
import re
import os
import sys
import codecs
from application import application
from duty        import duty
from commodity   import commodity
from hierarchy   import hierarchy
from docxcompose.composer import Composer
from docx import Document
from zipfile import ZipFile, ZIP_DEFLATED


word_filename = "/Users/matt.admin/projects/tariffs/tariff-reference/mfn_schedule/zipped_up.docx"
f.zipdir(word_filename)

