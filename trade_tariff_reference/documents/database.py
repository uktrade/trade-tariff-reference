import logging

from django.db import connections


logger = logging.getLogger(__name__)


class DatabaseConnect:

    @property
    def connection(self):
        return connections['tariff']

    def execute_sql(self, sql, only_one_row=False, dict_cursor=False):
        cur = self.connection.cursor()
        logger.debug(sql)
        cur.execute(sql)
        if dict_cursor:
            result = self.dict_cursor(cur)
        elif only_one_row:
            result = cur.fetchone()
        else:
            result = cur.fetchall()
        logger.debug(result)
        return result

    def shut_down(self):
        self.connection.close()

    def dict_cursor(self, cursor):
        description = [x[0] for x in cursor.description]
        for row in cursor:
            yield dict(zip(description, row))
