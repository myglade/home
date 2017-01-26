import logging

import db
from media import Media

log = logging.getLogger(__name__)

class ImageDb(db.Db):
    """
        name : file name
        path : relative path
        created : creation time of file
        loc : gps location string : "123.xxx,-23.xxx". latitude and longitude
    """
    table = "image"
    
    def __init__(self, db_file):
        super(ImageDb, self).__init__(db_file)

        self.execute('''CREATE TABLE IF NOT EXISTS %s(
                            id        INTEGER PRIMARY KEY AUTOINCREMENT,
                            name      TEXT,
                            path      TEXT,
                            created   DATETIME,
                            loc       TEXT)
                    ''' % self.table)
        
        self.execute("CREATE INDEX IF NOT EXISTS created_index on %s(created)" % self.table)
        
    def put(self, name, path, created, loc):
        self.execute("INSERT INTO %s(name,path,created,loc) VALUES(?,?,?,?)" % self.table,
                    (name, path, created, loc))
        self.commit()

    def get_next_by_time(self, id):
        """ by time """
        
        self.execute("SELECT * FROM %s WHERE id=?" % self.table, (id,))
        row = self.cursor.fetchone()
        if not row:
            self.execute("SELECT * FROM %s ORDER BY created, id LIMIT 1")
            row = self.cursor.fetchone()
            return row
        
        created = row["created"]
        self.execute('''SELECT * FROM %s WHERE id < ? AND created <= ? 
                        ORDER BY created, id LIMIT 1''' % self.table, 
                        (id, created))
        
        row = self.cursor.fetchone()
        # reach to the end. go back to first
        if not row:
            self.execute("SELECT * FROM %s ORDER BY created, id LIMIT 1")
        
        row = self.cursor.fetchone()
        
        return row
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)s.%(funcName)s %(levelname)s %(message)s')

    m = Media("media", "image")
    m.scan()
