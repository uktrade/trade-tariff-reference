from django.db import connections


class DatabaseConnect:

    def connect(self):
        self.conn = connections['tariff']

    def execute_sql(self, sql, only_one_row=False, dict_cursor=False):
        cur = self.conn.cursor()
        cur.execute(sql)
        if dict_cursor:
            result = self.dict_cursor(cur)
        elif only_one_row:
            result = cur.fetchone()
        else:
            result = cur.fetchall()
        return result

    def shutDown(self):
        self.conn.close()

    def dict_cursor(self, cursor):
        description = [x[0] for x in cursor.description]
        for row in cursor:
            yield dict(zip(description, row))