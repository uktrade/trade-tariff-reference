import sys, os
from docxcompose.composer import Composer
from docx import Document

# Define the parameters - document type
try:
	document_type = sys.argv[1]
except:
	document_type = "schedule"

if document_type == "s":
	document_type = "schedule"
elif document_type == "c":
	document_type = "classification"

# Define the parameters - start document
try:
	first_chapter = int(sys.argv[2])
except:
	first_chapter = 1
	
# Define the parameters - end document
try:
	last_chapter   = int(sys.argv[3])
except:
	last_chapter   = first_chapter
	
sChapter = str(first_chapter).zfill(2)
print ("Adding TOC")

BASE_DIR		= os.path.dirname(os.path.abspath(__file__))
COMPONENT_DIR	= os.path.join(BASE_DIR, "xmlcomponents")
SOURCE_DIR		= os.path.join(BASE_DIR, "source")
TOC_DIR			= os.path.join(SOURCE_DIR, "toc")
OUTPUT_DIR		= os.path.join(BASE_DIR, "output")
DEEP_DIR		= os.path.join(OUTPUT_DIR, document_type)

file_master = os.path.join(TOC_DIR, "toc_" + document_type + ".docx")
master = Document(file_master)
composer = Composer(master)
for s in range(first_chapter, last_chapter + 1):
	if s not in (77, 98, 99):
		sChapter = str(s).zfill(2)
		print ("Adding chapter " + sChapter)
		file_chapter = os.path.join(DEEP_DIR, document_type + "_" + sChapter + ".docx")
		doc1 = Document(file_chapter)
		composer.append(doc1)

file_out = os.path.join(DEEP_DIR, document_type + "_combined.docx")
composer.save(file_out)