from django.db import models


class Language(models.Model):
    oid = models.IntegerField(primary_key=True, db_column='oid')
    workbasket = models.IntegerField(db_column='workbasket_id')
    workbasket_sequence_number = models.IntegerField()
    status = models.TextField()
    operation = models.CharField(max_length=1)
    operation_date = models.DateField()
    validity_start_date = models.DateField()
    validity_end_date = models.DateField()
    language = models.CharField(max_length=2, db_column='language_id')

    class Meta:
        managed = False
        db_table = 'languages'

    def __str__(self):
        return self.language


class Measure(models.Model):
    oid = models.IntegerField(primary_key=True)
    ordernumber = models.CharField(max_length=255)
    geographical_area_sid = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'measures'

    def __str__(self):
        return f'{self.oid}'
