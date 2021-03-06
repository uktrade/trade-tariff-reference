# Generated by Django 2.2.4 on 2019-09-04 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0009_auto_20190830_1549'),
    ]

    operations = [
        migrations.AddField(
            model_name='agreement',
            name='last_checked',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='chapter',
            name='classification_last_checked',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='chapter',
            name='schedule_last_checked',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mfndocument',
            name='last_checked',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
