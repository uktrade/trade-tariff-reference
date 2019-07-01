# Import standard modules
import sys
import glob as g
import functions as f

# Set up
app = g.app
app.get_sections_chapters()
app.create_document()
app.shutDown()
