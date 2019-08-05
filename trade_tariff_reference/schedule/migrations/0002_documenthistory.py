# Generated by Django 2.2.2 on 2019-07-25 10:57

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('change', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, null=True)),
                ('forced', models.BooleanField()),
                ('agreement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedule.Agreement')),
                ('remote_file_name', models.CharField(blank=True, max_length=300, null=True)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
    ]
