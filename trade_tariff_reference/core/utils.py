import os

from django.conf import settings
from django.db import connections


def load_data_from_sql(filename, context_dict, database_name):
    file_path = os.path.join(settings.BASE_DIR, f'sql/{filename}')
    with open(file_path) as sql_file:
        sql_statement = sql_file.read()
        sql_statement = sql_statement.format(**context_dict)
        with connections[database_name].cursor() as cursor:
            cursor.execute(sql_statement)
            return cursor.fetchall()
