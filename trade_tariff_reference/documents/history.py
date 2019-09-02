import logging

from deepdiff import DeepDiff
from deepdiff.model import PrettyOrderedSet

from trade_tariff_reference.schedule.models import (
    AgreementDocumentHistory,
    ChapterDocumentHistory,
    MFNDocument,
    MFNDocumentHistory,
)

logger = logging.getLogger(__name__)


class AgreementDocumentHistoryLog:

    def __init__(self, obj, context, is_forced):
        self.object = obj
        self.context = context
        self.is_forced = is_forced
        self.history = self.get_history()

    @property
    def change(self):
        return self.get_change(getattr(self.history, 'data', None), self.context)

    def get_change(self, data, context):
        if not data:
            data = {}
        return DeepDiff(data, context)

    def prepare_change(self, change):
        if not change:
            return change
        for key in change.keys():
            if isinstance(change[key], PrettyOrderedSet):
                change[key] = list(change[key])
        return change

    def log_document_history(self, remote_file_name, obj=None):
        change = self.change
        if change:
            logger.debug(f'Changes found\n{change}')
        self.create_history_event(change, remote_file_name)

    def get_history(self):
        return AgreementDocumentHistory.objects.filter(
            agreement=self.object,
        ).first()

    def create_history_event(self, change, remote_file_name):
        AgreementDocumentHistory.objects.create(
            agreement=self.object,
            data=self.context,
            change=self.prepare_change(change),
            forced=self.is_forced,
            remote_file_name=remote_file_name,
        )


class ChapterDocumentHistoryLog(AgreementDocumentHistoryLog):

    def __init__(self, obj, context, is_forced, document_type):
        self.document_type = document_type
        super().__init__(obj, context, is_forced)

    def get_history(self):
        return ChapterDocumentHistory.objects.filter(
            chapter=self.object,
            document_type=self.document_type,
        ).first()

    def create_history_event(self, change, remote_file_name, obj=None):
        ChapterDocumentHistory.objects.create(
            chapter=self.object,
            document_type=self.document_type,
            data=self.context,
            change=self.prepare_change(change),
            forced=self.is_forced,
            remote_file_name=remote_file_name,
        )


class MFNDocumentHistoryLog(AgreementDocumentHistoryLog):

    def __init__(self, obj, context, is_forced, document_type):
        self.document_type = document_type
        super().__init__(obj, context, is_forced)

    def get_history(self):
        return MFNDocumentHistory.objects.filter(
            mfn_document=self.object,
            document_type=self.document_type,
        ).first()

    def create_history_event(self, change, remote_file_name):
        MFNDocumentHistory.objects.create(
            mfn_document=self.get_object(),
            document_type=self.document_type,
            data=self.context,
            change=self.prepare_change(change),
            forced=self.is_forced,
            remote_file_name=remote_file_name,
        )

    def get_object(self):
        if self.object:
            return self.object
        return MFNDocument.objects.get(document_type=self.document_type)
