# Generated by Django 2.2.2 on 2019-08-12 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0005_auto_20190808_1141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='extendedquota',
            name='addendum',
            field=models.CharField(blank=True, default='', max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='extendedquota',
            name='measurement_unit_code',
            field=models.CharField(blank=True, default='', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='extendedquota',
            name='scope',
            field=models.CharField(blank=True, default='', max_length=1000, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='extendedquota',
            unique_together={('agreement', 'quota_order_number_id')},
        ),
    ]