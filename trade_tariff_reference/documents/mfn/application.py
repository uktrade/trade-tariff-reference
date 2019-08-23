import os

from trade_tariff_reference.documents.database import DatabaseConnect
from trade_tariff_reference.schedule.models import LatinTerm, SpecialNote

from .chapter import process_chapter
from .constants import (
    CUCUMBER_COMMODITY_CODES,
    GET_AUTHORISED_USE_COMMODITIES,
    GET_SECTION_CHAPTERS,
    SCHEDULE,
)


class Application(DatabaseConnect):

    def __init__(self, document_type, first_chapter=1, last_chapter=99):
        self.document_type = document_type
        self.first_chapter = first_chapter
        self.last_chapter = last_chapter
        self.authorised_use_list = []
        self.special_list = []
        self.section_chapter_list = []
        self.suppress_duties = False
        self.latin_phrases = []

        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.SOURCE_DIR = os.path.join(self.BASE_DIR, "source")
        self.MODEL_DIR = os.path.join(self.BASE_DIR, "model")

    def main(self):
        self.latin_phrases = self.get_latin_phrases()
        self.section_chapter_list = self.get_sections_chapters()
        if self.document_type == SCHEDULE:
            self.authorised_use_list = self.get_authorised_use_commodities()
            self.special_list = self.get_special_notes()
        for i in range(self.first_chapter, self.last_chapter + 1):
            process_chapter(self, i)
        self.shut_down()

    def get_latin_phrases(self):
        return list(LatinTerm.objects.values_list('text', flat=True))

    def get_sections_chapters(self):
        rows = self.execute_sql(GET_SECTION_CHAPTERS, dict_cursor=True)
        section_chapter_list = []
        for row in rows:
            section_chapter_list.append([row['chapter'], row['section_id'], False])
        return section_chapter_list

    def get_authorised_use_commodities(self):
        # This function is required - this is used to identify any commodity codes
        # where there has been a 105 measure type assigned since the start of 2018
        # (up to the end of 2019), i.e. taking into account the measures that were
        # in place before No Deal Brexit

        # If a commodity code has a 105 instead of a 103 assigned to it, this means that there is
        # a need to insert an authorised use message in the notes column for the given commodity
        authorised_use_list = []
        rows = self.execute_sql(GET_AUTHORISED_USE_COMMODITIES, dict_cursor=True)
        for row in rows:
            authorised_use_list.append(row['goods_nomenclature_item_id'])

        # Also add in cucumbers: the data cannot find these, therefore manually added,
        # as per instruction from David Owen
        authorised_use_list.extend(CUCUMBER_COMMODITY_CODES)
        return authorised_use_list

    def get_special_notes(self):
        # This function is required - it looks in the file  special_notes.csv
        # and finds a list of commodities with 'special 'notes that go alongside them
        # In actual fact, there is only one record in here at the point of
        # writing this note - 5701109000,"Dutiable surface shall not include the heading,
        # the selvedges and the fringes"
        return list(SpecialNote.objects.all())