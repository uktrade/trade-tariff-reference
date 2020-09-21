import copy

from django.db.models.fields.files import FieldFile
from django.shortcuts import reverse

import pytest

from rest_framework import status

from trade_tariff_reference.schedule.tests.factories import (
    AgreementDocumentHistoryFactory,
    AgreementFactory,
    ChapterDocumentHistoryFactory,
    ChapterFactory,
    ChapterNoteFactory,
    ExtendedQuotaFactory,
    LatinTermFactory,
    MFNDocumentHistoryFactory,
    MFNTableOfContentFactory,
    SpecialNoteFactory,
)

pytestmark = pytest.mark.django_db


def get_factory_dict(factory):
    factory_dict = copy.deepcopy(factory.__dict__)
    remove_keys = ['_state']

    for key, value in list(factory_dict.items()):
        if isinstance(value, FieldFile):
            remove_keys.append(key)
        if not value:
            factory_dict[key] = ''
        if key.endswith('_id') and key not in ['quota_order_number_id']:
            new_key = key.replace('_id', '')
            factory_dict.pop(key)
            factory_dict[new_key] = value
    for key in remove_keys:
        factory_dict.pop(key)
    return factory_dict


@pytest.mark.parametrize(
    'url,include_kwargs,post',
    (
        ('admin:schedule_agreementdocumenthistory_add', False, {}),
        ('admin:schedule_agreementdocumenthistory_changelist', False, {}),
        ('admin:schedule_agreementdocumenthistory_change', True, {}),

        ('admin:schedule_chapterdocumenthistory_add', False, {}),
        ('admin:schedule_chapterdocumenthistory_changelist', False, {}),
        ('admin:schedule_chapterdocumenthistory_change', True, {}),

        ('admin:schedule_mfndocumenthistory_add', False, {}),
        ('admin:schedule_mfndocumenthistory_changelist', False, {}),
        ('admin:schedule_mfndocumenthistory_change', True, {}),

        ('admin:schedule_latinterm_add', False, {}),
        ('admin:schedule_latinterm_changelist', False, {}),
        ('admin:schedule_latinterm_change', True, {'text': 'hello'}),

        ('admin:schedule_specialnote_add', False, {}),
        ('admin:schedule_specialnote_changelist', False, {}),
        ('admin:schedule_specialnote_change', True, {'note': 'special note'}),

        ('admin:schedule_agreement_add', False, {}),
        ('admin:schedule_agreement_changelist', False, {}),
        ('admin:schedule_agreement_change', True, {'version': '2.0'}),

        ('admin:schedule_chapternote_add', False, {}),
        ('admin:schedule_chapternote_changelist', False, {}),
        ('admin:schedule_chapternote_change', True, {}),

        ('admin:schedule_chapter_add', False, {}),
        ('admin:schedule_chapter_changelist', False, {}),
        ('admin:schedule_chapter_change', True, {'description': 'description'}),

        ('admin:schedule_extendedquota_add', False, {}),
        ('admin:schedule_extendedquota_changelist', False, {}),
        ('admin:schedule_extendedquota_change', True, {'scope': 'test scope'}),

        ('admin:schedule_mfntableofcontent_add', False, {}),
        ('admin:schedule_mfntableofcontent_changelist', False, {}),
        ('admin:schedule_mfntableofcontent_change', True, {}),
    ),
)
def test_admin_views(
    authenticated_admin_client,
    url,
    include_kwargs,
    post,
):
    if 'agreementdocumenthistory' in url:
        factory = AgreementDocumentHistoryFactory()
    elif '_agreement_' in url:
        factory = AgreementFactory()
    elif 'chapterdocumenthistory' in url:
        factory = ChapterDocumentHistoryFactory()
    elif 'latinterm' in url:
        factory = LatinTermFactory()
    elif 'specialnote' in url:
        factory = SpecialNoteFactory()
    elif 'chapternote' in url:
        factory = ChapterNoteFactory()
    elif '_chapter_' in url:
        factory = ChapterFactory()
    elif '_extendedquota_' in url:
        factory = ExtendedQuotaFactory()
    elif 'mfntableofcontent' in url:
        factory = MFNTableOfContentFactory()
    else:
        factory = MFNDocumentHistoryFactory()

    kwargs = {}
    if include_kwargs:
        kwargs = {'object_id': factory.pk}

    uri = reverse(url, kwargs=kwargs)
    response = authenticated_admin_client.get(uri)
    assert response.status_code == status.HTTP_200_OK

    if post:
        post_data = get_factory_dict(factory)
        post_data.update(post)
        post_response = authenticated_admin_client.post(uri, data=post_data, follow=True)
        assert post_response.status_code == status.HTTP_200_OK
        assert b'errorlist' not in post_response.content, str(post_response.content)

        factory.refresh_from_db()
        for key, value in post.items():
            assert getattr(factory, key) == value
