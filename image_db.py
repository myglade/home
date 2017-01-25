import db

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
        
        self.execute("CREATE INDEX created_index on %s(created)" % self.table)
        
    def put(self, name, path, created, loc):
        set.execute("INSERT INTO %s(name,path,created,loc) VALUES(?,?,?,?)" % self.table,
                    (name, path, created, loc))
        
    def get_next_by_time(self, id):
        """ by time """
        
        self.execute("SELECT * FROM %s WHERE id=?" % self.table, (id,))
        row = self.cursor.fetchone()
        if not row:
            self.execute("SELECT * FROM %s ORDER BY created, id LIMIT 1")
            row = self.cursor.fetchone()
            return row
        
        created = row[3]
        self.execute('''SELECT * FROM %s WHERE id < ? AND created <= ? 
                        ORDER BY created, id LIMIT 1''' % self.table, 
                        (id, created))
        
        row = self.cursor.fetchone()
        # reach to the end. go back to first
        if not row:
            self.execute("SELECT * FROM %s ORDER BY created, id LIMIT 1")
        
        row = self.cursor.fetchone()
        
        return row
    
    