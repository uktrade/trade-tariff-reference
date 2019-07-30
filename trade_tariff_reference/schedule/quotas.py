import csv
from collections.abc import Mapping
from io import StringIO

from .constants import (
    LICENSED_QUOTA_FIELDS,
    ORIGIN_QUOTA_FIELDS,
    SCOPE_QUOTA_FIELDS,
    STAGING_QUOTA_FIELDS,
)
from .models import ExtendedQuota


def process_csv_input(data, header, is_origin_quota=False, is_licensed_quota=False):
    f = StringIO(data)
    reader = csv.reader(f, delimiter=',')
    rows = [dict(zip(header, row)) for row in reader]
    response = {}
    for row in rows:
        quota_order_number_id = row.pop('quota_order_number_id', None)
        if not quota_order_number_id:
            continue
        if quota_order_number_id not in response:
            response[quota_order_number_id] = {}
        response[quota_order_number_id].update(row)
        if is_origin_quota:
            response[quota_order_number_id]['is_origin_quota'] = True
        if is_licensed_quota:
            response[quota_order_number_id]['quota_type'] = ExtendedQuota.LICENSED
    return response


def dict_merge(original_dict, merge_dict):
    for k, v in merge_dict.items():
        if isinstance(original_dict.get(k), dict) and isinstance(v, Mapping):
            original_dict[k] = dict_merge(original_dict[k], v)
        else:
            original_dict[k] = v
    return original_dict


def process_quotas(quotas):
    processed_quota_data = {}
    if quotas.get('origin_quotas'):
        processed_quota_data = dict_merge(processed_quota_data, _process_origin_quotas(quotas['origin_quotas']))

    if quotas.get('licensed_quotas'):
        processed_quota_data = dict_merge(
            processed_quota_data, _process_licensed_quotas(quotas['licensed_quotas'])
        )

    if quotas.get('scope_quotas'):
        processed_quota_data = dict_merge(
            processed_quota_data, _process_scope_quotas(quotas['scope_quotas'])
        )

    if quotas.get('staging_quotas'):
        processed_quota_data = dict_merge(
            processed_quota_data, _process_staging_quotas(quotas['staging_quotas'])
        )
    return processed_quota_data


def _process_origin_quotas(quotas):
    return process_csv_input(quotas, ORIGIN_QUOTA_FIELDS, is_origin_quota=True)


def _process_licensed_quotas(quotas):
    return process_csv_input(
        quotas, LICENSED_QUOTA_FIELDS, is_licensed_quota=True
    )


def _process_scope_quotas(quotas):
    return process_csv_input(quotas, SCOPE_QUOTA_FIELDS)


def _process_staging_quotas(quotas):
    return process_csv_input(quotas, STAGING_QUOTA_FIELDS)
