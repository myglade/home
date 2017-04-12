import logging
import sqlite3

import config
from media import Media

from pymysql.err import *
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta
from sqlalchemy import *
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker

from db import Base

log = logging.getLogger(config.logname)


class Image(Base):
    __tablename__ = "image"
    __table_args__ = (Index('created_index', "created"), )

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    '''
    If anyone is having issues with INNODB / Utf-8 trying to put 
    an UNIQUE index on a VARCHAR(256) field, switch it to VARCHAR(255). 
    It seems 255 is the limitation.
    '''
    path = Column(String(255), unique=True, nullable=False)
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
    #table = "image"
    
    def __init__(self, db):
        self.db = db
        self.session = db.session
        
    def reset(self):
        self.session.query(Image).delete()
        self.session.commit()

    def put(self, name, path, created, loc):
        created_time = created
        # datetime(2017, 12, 5)
        image = Image(name=name, path=path, created=created_time, loc=loc)
        try:
            self.session.add(image)
            self.session.commit()
        except Exception as e:
            log.info(e)

    def get_next_by_time(self, id):
        """ by time """
        
        image = self.session.query(Image).filter(Image.id == id).first()
        if not image:
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
    from db import Db

    image_info = image_info.ImageInfo()

    db = Db()
    imagedb = ImageDb(db)
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
        image = imagedb.get_next_by_time(id)
        print "+++++++++++++++++++++++++++++", image
        id = image.id

'''
{'loc': u'37.350078,-121.981169', 
'path': u'media/1.jpg', 
'created': u'2015:10:03 01:31:01', 
'id': 1, 
'name': u'1.jpg'}

'''