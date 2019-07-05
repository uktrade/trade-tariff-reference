from django.db import connections


class DatabaseConnect:

    def connect(self):
        self.conn = connections['tariff']

    def execute_sql(self, sql, only_one_row=False):
        cur = self.conn.cursor()
        cur.execute(sql)
        if only_one_row:
            return cur.fetchone()
        return cur.fetchall()

    def shutDown(self):
        self.conn.close()
