from datetime import datetime

from django.db import migrations
from django.conf import settings
from trade_tariff_reference.core.utils import load_data_from_sql


def load_database_function(apps, schema_editor):
    # Only run if the tariff database is managed.
    # This skips this migration for testing as we pretend in testing that the view
    # is a database model so we don't want to create the database view.
    if settings.MANAGE_TARIFF_DATABASE:
        return

    load_data_from_sql('goods_nomenclature_export.sql', {}, 'tariff')


class Migration(migrations.Migration):

    dependencies = [
        ('tariff', '0008_simplecurrentmeasures'),
    ]

    operations = [
        migrations.RunPython(load_database_function, migrations.RunPython.noop),
    ]
