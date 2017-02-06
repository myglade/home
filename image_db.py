import logging
import sqlite3

import db
from media import Media
from _sqlite3 import Row

log = logging.getLogger(__name__)

class ImageDb(db.Db):
    """
        name : file name
        path : relative path
        created : creation time of file
        loc : gps location string : "123.xxx,-23.xxx". latitude and longitude
    """
    table = "image"
    
    def __init__(self, db_file, conn=None):
        super(ImageDb, self).__init__(db_file, conn)

        self.execute('''CREATE TABLE IF NOT EXISTS %s(
                            id        INTEGER PRIMARY KEY AUTOINCREMENT,
                            name      TEXT,
                            path      TEXT UNIQUE,
                            created   DATETIME,
                            loc       TEXT)
                    ''' % self.table)
        
        self.execute("CREATE INDEX IF NOT EXISTS created_index on %s(created)" % self.table)
        
    def put(self, name, path, created, loc):
        try:
            self.execute("INSERT INTO %s(name,path,created,loc) VALUES(?,?,?,?)" % self.table,
                        (name, path, created, loc))
            
            log.debug("Insert name=%s, path=%s, created=%s, loc=%s", name, path, created, loc)
            self.commit()
        except sqlite3.IntegrityError:
            log.info("image already exists. name=%s, path=%s, created=%s, loc=%s", 
                     name, path, created, loc)

    def get_next_by_time(self, id):
        """ by time """
        
        self.execute("SELECT * FROM %s WHERE id=?" % self.table, (id,))
        row = self.cursor.fetchone()
        if not row:
            self.execute("SELECT * FROM %s ORDER BY created, id LIMIT 1" % self.table)
            row = self.cursor.fetchone()
            return row
        
        created = row["created"]
        # if there are image with the same times, get next
        self.execute('''SELECT * FROM %s WHERE id > ? AND created=? 
                ORDER BY id LIMIT 1''' % self.table, 
                (id, created))
        row = self.cursor.fetchone()
        if row:
            return row  

        # get next earliest image
        self.execute('''SELECT * FROM %s WHERE created > ? 
                        ORDER BY created, id LIMIT 1''' % self.table, 
                        (created, ))
        
        row = self.cursor.fetchone()
        if row:
            return row  
        
        # reach to the end. go back to first
        self.execute("SELECT * FROM %s ORDER BY created, id LIMIT 1" % self.table)
        row = self.cursor.fetchone()
        
        return row
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)s.%(funcName)s %(levelname)s %(message)s')

    import image_info

    imagedb = ImageDb("image.sqlite")
    m = Media("media", "image")
    media_list = m.scan()
    for value in media_list.values():
        for name in value.file_path.keys():
            path = name
            break

        date, loc = image_info.get_img_info(path)
        imagedb.put(value.fullname(), path, date, loc)

    id = -1
    for i in xrange(20):
        r = imagedb.get_next_by_time(id)
        print r
        id = r["id"]

'''
{'loc': u'37.350078,-121.981169', 
'path': u'media/1.jpg', 
'created': u'2015:10:03 01:31:01', 
'id': 1, 
'name': u'1.jpg'}

'''