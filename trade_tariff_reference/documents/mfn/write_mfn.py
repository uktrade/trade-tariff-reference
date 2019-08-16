# Import standard modules
from __future__ import with_statement
import psycopg2
from contextlib import closing
from zipfile import ZipFile, ZIP_DEFLATED
import os
import sys
import codecs
import re
import functions

# Import custom modules
from application import application
from chapter     import chapter

app = functions.app
app.get_sections_chapters()
app.read_templates()

if app.document_type == "schedule":
	app.get_authorised_use_commodities()
	app.getSeasonal()
	app.get_special_notes()

for i in range(app.first_chapter, app.last_chapter + 1):
	oChapter = chapter(i)
	oChapter.format_chapter()

app.db_disconnect()
