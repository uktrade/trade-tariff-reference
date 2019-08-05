# Generated by Django 2.2.2 on 2019-07-24 13:45

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion

import trade_tariff_reference.schedule.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Agreement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(unique=True, verbose_name='Unique ID')),
                ('country_codes', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=6), size=None)),
                ('geographical_area', models.CharField(blank=True, max_length=200, null=True)),
                ('agreement_name', models.CharField(max_length=1024, verbose_name='Agreement title')),
                ('agreement_date', models.DateField()),
                ('version', models.CharField(max_length=20)),
                ('country_name', models.CharField(max_length=200)),
                ('document', models.FileField(blank=True, null=True, upload_to='', storage=trade_tariff_reference.schedule.models.DocumentStorage())),
                ('document_created_at', models.DateTimeField(blank=True, null=True)),

            ],
        ),
    ]
