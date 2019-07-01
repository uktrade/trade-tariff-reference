import psycopg2


class DatabaseConnect:

    def connect(self):
        self.conn = psycopg2.connect(
            "dbname=" + self.DBASE + " user=postgres password=" + self.p + " host=postgres"
        )

    def shutDown(self):
        self.conn.close()