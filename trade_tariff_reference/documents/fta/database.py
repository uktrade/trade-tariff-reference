from django.db import connections

import trade_tariff_reference.documents.fta.functions as f


class DatabaseConnect:

    def connect(self):
        self.conn = connections['tariff']

    def execute_sql(self, sql, only_one_row=False, dict_cursor=False):
        cur = self.conn.cursor()
        f.log(sql)
        cur.execute(sql)
        if dict_cursor:
            result = self.dict_cursor(cur)
        elif only_one_row:
            result = cur.fetchone()
        else:
            result = cur.fetchall()
        f.log(result)
        return result

    def shutDown(self):
        self.conn.close()

    def dict_cursor(self, cursor):
        description = [x[0] for x in cursor.description]
        for row in cursor:
            yield dict(zip(description, row))
