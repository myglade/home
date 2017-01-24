import logging
import sqlite3

log = logging.getLogger(__name__)

class Db(object):
    """ database """
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = sqlite3.connect(db_file)
        # except lite.Error, e:

    def execute(self, sql):
        log.debug("execute: %s", sql)
        return self.conn.execute(sql)

    def insert(self, table, data):
        """
        table (str) : table name
        data (dict) : values
        """

        sql = ""
        key = ""
        values = ""
        param = ()
        for col, val in data.iteritems():
            key += "," + col
            values += ",?"
            param += (val)

        sql = "INSERT INTO %s (%s) VALUES(%s)"
        self.conn.execute(sql)