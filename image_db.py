import logging
import sqlite3

import config
from media import Media
from _sqlite3 import Row

log = logging.getLogger(config.logname)

from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta
from sqlalchemy import *
from db import Base

from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker

class Image(Base):
    __tablename__ = "image"
    __table_args__ = (Index('created_index', "created"), )

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    path = Column(String(512), nullable=False)
    created = Column(DateTime, nullable=False)
    loc = Column(String(128))

    def __repr__(self):
        created = self.created.strftime("%Y-%m-%d %H:%M:%S")
        return "<Image (id=%d, name='%s', path='%s', created='%s', loc='%s')>" % \
                (self.id, self.name, self.path, created, self.loc)

class ImageDb(object):
    """
        name : file name
        path : relative path
        created : creation time of file
        loc : gps location string : "123.xxx,-23.xxx". latitude and longitude
    """
    table = "image"
    
    def __init__(self, db):
        self.db = db
        self.session = db.session
        
    def reset(self):
        self.execute("DELETE FROM %s" % self.table)
        self.execute("vacuum");

    def put(self, name, path, created, loc):
        created_time = created
        # datetime(2017, 12, 5)
        image = Image(name=name, path=path, created=created_time, loc=loc)
        self.session.add(image)
        self.session.commit()

    def get_next_by_time(self, id):
        """ by time """
        
        count = self.session.query(Image).filter(Image.id == id).count()
        if not count:
            image = self.session.query(Image).order_by(Image.created).first()
            return image

        created = image.created
        image = self.session.query(Image).\
                filter(and_(Image.id > id, Image.created == created)).\
                order_by(Image.id).first()

        if image:
            return image

        image = self.session.query(Image).\
                filter(Image.created > created).\
                order_by(Image.created, Image.id).first()

        if image:
            return image

        image = self.session.query(Image).\
                order_by(Image.created, Image.id).first()

        return image
"""
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
"""

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

        date, loc = image_info.get(path)
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