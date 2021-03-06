# Generated by Django 2.2.2 on 2019-08-30 15:49

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import trade_tariff_reference.schedule.models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0008_chapter_chapternote'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChapterDocumentHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('change', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, null=True)),
                ('forced', models.BooleanField()),
                ('remote_file_name', models.CharField(blank=True, max_length=300, null=True)),
                ('document_type', models.CharField(choices=[('schedule', 'Schedule'), ('classification', 'Classification')], max_length=100)),
            ],
            options={
                'verbose_name_plural': 'Chapter Document Histories',
            },
        ),
        migrations.CreateModel(
            name='MFNDocument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.FileField(storage=trade_tariff_reference.schedule.models.MFNStorage(), upload_to='')),
                ('document_created_at', models.DateTimeField()),
                ('document_check_sum', models.CharField(max_length=32)),
                ('document_type', models.CharField(choices=[('schedule', 'Schedule'), ('classification', 'Classification')], max_length=100)),
                ('document_status', models.CharField(choices=[('available', 'Available'), ('unavailable', 'Unavailable'), ('generating', 'Generating')], default='unavailable', max_length=20)),
            ],
        ),
        migrations.RenameModel(
            old_name='DocumentHistory',
            new_name='AgreementDocumentHistory',
        ),
        migrations.AlterModelOptions(
            name='agreementdocumenthistory',
            options={'verbose_name_plural': 'Agreement Document Histories'},
        ),
        migrations.AlterModelOptions(
            name='chapter',
            options={'ordering': ('id',)},
        ),
        migrations.AddField(
            model_name='chapter',
            name='classification_document_check_sum',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='chapter',
            name='schedule_document_check_sum',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='chapternote',
            name='document_check_sum',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.CreateModel(
            name='MFNDocumentHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('change', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, null=True)),
                ('forced', models.BooleanField()),
                ('remote_file_name', models.CharField(blank=True, max_length=300, null=True)),
                ('document_type', models.CharField(choices=[('schedule', 'Schedule'), ('classification', 'Classification')], max_length=100)),
                ('mfn_document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedule.MFNDocument')),
            ],
            options={
                'verbose_name_plural': 'MFN Document Histories',
            },
        ),
        migrations.AddConstraint(
            model_name='mfndocument',
            constraint=models.UniqueConstraint(fields=('document_type',), name='MFN Document Type constraint'),
        ),
        migrations.AddField(
            model_name='chapterdocumenthistory',
            name='chapter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedule.Chapter'),
        ),
    ]
