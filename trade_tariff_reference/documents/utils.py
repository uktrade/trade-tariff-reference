import uuid

from django.core.files.base import ContentFile
from django.utils import timezone


def upload_document_to_s3(agreement, local_file_name):
    remote_file_name = f'{uuid.uuid4()}.docx'
    with open(local_file_name, 'rb') as local_file:
        contents = ContentFile(local_file.read())
        agreement.document.save(remote_file_name, contents, save=True)
        agreement.document_created_at = timezone.now()
        agreement.save(update_fields=['document_created_at'])
    return remote_file_name


def upload_generic_document_to_s3(model, field_name, local_file_name, remote_file_name):
    with open(local_file_name, 'rb') as local_file:
        contents = ContentFile(local_file.read())
        field = getattr(model, field_name)
        field.save(remote_file_name, contents, save=True)
        created_at_field = f'{field_name}_created_at'
        setattr(model, created_at_field, timezone.now())
        model.save(update_fields=[created_at_field])
    return remote_file_name


def update_agreement_document_status(agreement, status):
    agreement.document_status = status
    agreement.save(update_fields=['document_status'])
