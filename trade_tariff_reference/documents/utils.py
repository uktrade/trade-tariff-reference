import hashlib
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
        file_contents = local_file.read()
        new_check_sum = get_document_check_sum(file_contents)
        check_sum_field = f'{field_name}_check_sum'
        if getattr(model, check_sum_field) != new_check_sum:
            contents = ContentFile(file_contents)
            created_at_field = f'{field_name}_created_at'
            setattr(model, check_sum_field, new_check_sum)
            setattr(model, created_at_field, timezone.now())
            model.save()
            field = getattr(model, field_name)
            field.save(remote_file_name, contents, save=True)
    return remote_file_name


def update_document_status(model, status):
    model.document_status = status
    model.save(update_fields=['document_status'])


def update_last_checked(model):
    model.last_checked = timezone.now()
    model.save(update_fields=['last_checked'])


def get_document_check_sum(file_contents):
    document_hash = hashlib.md5(file_contents)
    return document_hash.hexdigest()
