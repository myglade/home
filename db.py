import config
import logging
import sqlite3

log = logging.getLogger(config.log)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class Db(object):
    """ database """
    def __init__(self, db_file, conn=None):
        if conn:
            self.conn = conn
        else:
            self.db_file = db_file
            self.conn = sqlite3.connect(db_file)
            
        self.conn.row_factory = dict_factory
        # or conn.row_factory = sqlite3.Row

        self.cursor = self.conn.cursor()
        # except lite.Error, e:

    def __del__(self):
        if self.conn:
            self.conn.close()
            del self.conn
                     
    def execute(self, *args):
        self.cursor.execute(*args)
        
    def commit(self):
        self.conn.commit()