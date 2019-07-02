from django.db import connections


class DatabaseConnect:

    def connect(self):
        self.conn = connections['tariff']

    def shutDown(self):
        self.conn.close()
