from deepdiff.model import PrettyOrderedSet

import pytest

from trade_tariff_reference.documents.history import (
    AgreementDocumentHistoryLog,
    ChapterDocumentHistoryLog,
    MFNDocumentHistoryLog,
)
from trade_tariff_reference.documents.mfn.constants import (
    CLASSIFICATION,
    SCHEDULE,
)
from trade_tariff_reference.schedule.models import (
    AgreementDocumentHistory,
    ChapterDocumentHistory,
    MFNDocumentHistory,
)
from trade_tariff_reference.schedule.tests.factories import (
    AgreementFactory,
    ChapterFactory,
    MFNDocumentFactory,
)

pytestmark = pytest.mark.django_db


class TestAgreementDocumentHistoryLog:

    def get_document_history_log(self, *args):
        return AgreementDocumentHistoryLog(*args)

    def get_object(self):
        return AgreementFactory()

    def test_change_without_history(self):
        agreement = self.get_object()
        history = self.get_document_history_log(agreement, {'version': '2.0'}, False)
        assert history.change == {'dictionary_item_added': ["root['version']"]}

    def test_get_change(self):
        history = self.get_document_history_log(None, {}, None)
        result = history.get_change({'version': '1.0'}, {'version': '2.0'})
        assert result == {
            'values_changed': {
                "root['version']": {
                    'new_value': '2.0',
                    'old_value': '1.0',
                },
            },
        }

    @pytest.mark.parametrize(
        'change,expected_result',
        (
            (None, None),
            ({'version': '2.0'}, {'version': '2.0'}),
            ({'version': PrettyOrderedSet(['1', '2'])}, {'version': ['1', '2']}),
        )
    )
    def test_prepare_change(self, change, expected_result):
        history = self.get_document_history_log(None, {}, None)
        assert history.prepare_change(change) == expected_result

    def test_create_history_event(self):
        forced = False
        agreement = self.get_object()
        history = self.get_document_history_log(agreement, {'version': '2.0'}, forced)
        change = {'change': 'version 1'}
        remote_file_name = 'test_remote1.txt'
        history.create_history_event(change, remote_file_name)
        self._assert_document_history(agreement, change, remote_file_name, forced)

    def _assert_document_history(self, agreement, change, remote_file_name, forced):
        actual_history = AgreementDocumentHistory.objects.get(
            agreement=agreement
        )
        assert actual_history.change == change
        assert actual_history.remote_file_name == remote_file_name
        assert actual_history.forced == forced

    def test_log_document_history(self, caplog):
        forced = True
        remote_file_name = 'test_log_document_history.txt'
        agreement = self.get_object()
        history = self.get_document_history_log(agreement, {'version': '2.0'}, forced)
        caplog.set_level('DEBUG')
        history.log_document_history(remote_file_name)
        log_output = caplog.text.lower()
        assert "{'dictionary_item_added': [root['version']]}" in log_output
        expected_change = {'dictionary_item_added': ["root['version']"]}
        self._assert_document_history(agreement, expected_change, remote_file_name, forced)


class TestChapterDocumentHistoryLog(TestAgreementDocumentHistoryLog):
    document_type = SCHEDULE

    def get_document_history_log(self, *args):
        return ChapterDocumentHistoryLog(*args, self.document_type)

    def get_object(self):
        return ChapterFactory()

    def _assert_document_history(self, chapter, change, remote_file_name, forced):
        actual_history = ChapterDocumentHistory.objects.get(
            chapter=chapter,
        )
        assert actual_history.change == change
        assert actual_history.remote_file_name == remote_file_name
        assert actual_history.forced == forced
        assert actual_history.document_type == self.document_type


class TestMFNDocumentHistoryLog(TestAgreementDocumentHistoryLog):
    document_type = CLASSIFICATION

    def get_document_history_log(self, *args):
        return MFNDocumentHistoryLog(*args, self.document_type)

    def get_object(self):
        return MFNDocumentFactory(document_type=self.document_type)

    def _assert_document_history(self, mfn_document, change, remote_file_name, forced):
        actual_history = MFNDocumentHistory.objects.get(
            mfn_document=mfn_document,
        )
        assert actual_history.change == change
        assert actual_history.remote_file_name == remote_file_name
        assert actual_history.forced == forced
        assert actual_history.document_type == self.document_type

    def test_create_history_event_when_mfn_document_does_not_exist(self):
        forced = False
        history = self.get_document_history_log(None, {'version': '2.0'}, forced)
        change = {'change': 'version 1'}
        remote_file_name = 'test_remote1.txt'
        mfn_document = self.get_object()
        history.create_history_event(change, remote_file_name)
        self._assert_document_history(mfn_document, change, remote_file_name, forced)
