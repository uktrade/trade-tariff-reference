import uuid

from django.core.files.base import ContentFile
from django.utils import timezone


def upload_document_to_s3(agreement, local_file_name):
    remote_file_name = f'{uuid.uuid4()}.docx'
    with open(local_file_name, 'rb') as local_file:
        contents = ContentFile(local_file.read())
        agreement.document.save(remote_file_name, contents, save=True)
        agreement.document_created_at = timezone.now()
        agreement.save()
    return remote_file_name