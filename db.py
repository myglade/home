import logging
import sqlite3

log = logging.getLogger(__name__)

class Db(object):
    """ database """
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        # except lite.Error, e:

    def execute(self, *args):
        self.cursor.execute(*args)
        
    def commit(self):
        self.conn.commit()