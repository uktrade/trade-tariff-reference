from django.core.management.base import BaseCommand

from trade_tariff_reference.documents import database

SQL = "SELECT table_name FROM information_schema.columns WHERE column_name = 'operation_date' and table_name like '%_oplog'"

UPDATE = "UPDATE {table_name} SET status = 'published' WHERE status IS NULL OR status = ''"


UPDATE_S = """Declare @Rowcount INT = 1;

WHILE (@@Rowcount > 0)   
BEGIN
        UPDATE TOP (100000) {table_name} SET status = 'published' WHERE status IS NULL OR status = ''
        SET @@Rowcount = @@ROWCOUNT;
       CHECKPOINT;   --<-- to commit the changes with each batch
END
"""


class Command(BaseCommand):

    help = ''

    def handle(self, *args, **options):
        db = database.DatabaseConnect()
        result = db.execute_sql(SQL, dict_cursor=True)
        result = list(result)
        for table_dict in result:
            table_sql = UPDATE.format(table_name=table_dict['table_name'])
            print(table_dict['table_name'])
            result = db.execute_sql(table_sql, dict_cursor=True)
