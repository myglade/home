import sqlite3

class Db(object):
    """ database """
    def __init__(self, name):
        pass

    def _create_table(name, columns):
        pass

    def create_image_table():
        pass

    def create_media_table():
        pass


    def exectue(self, *args):
        self.cursor.execute(*args)
        
    def commit(self):
        self.conn.commit()