import logging
import sqlite3

import config
from media import Media

# from pymysql.err import *
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta
from sqlalchemy import *
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker, class_mapper, ColumnProperty
import time
import sys
from sqlalchemy import exc

from db import Base

log = logging.getLogger(config.logname)


class Image(Base):
    __tablename__ = "image"
    __table_args__ = (Index("created_index", "created"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    """
    If anyone is having issues with INNODB / Utf-8 trying to put 
    an UNIQUE index on a VARCHAR(256) field, switch it to VARCHAR(255). 
    It seems 255 is the limitation.
    """
    path = Column(String(255), unique=True, nullable=False)
    created = Column(DateTime, nullable=False)
    media_type = Column(Integer)
    ext = Column(String(64))
    loc = Column(String(128))
    flag = Column(Integer, default=0)

    def __repr__(self):
        return "<Image (id=%s, name='%s', path='%s', created='%s', media_type='%s', ext='%s', loc='%s', flag=%s)>" % (
            self.id,
            self.name,
            self.path,
            self.created,
            self.media_type,
            self.ext,
            self.loc,
            self.flag,
        )

    def as_dict(self):
        result = {}
        for prop in class_mapper(self.__class__).iterate_properties:
            if isinstance(prop, ColumnProperty):
                result[prop.key] = getattr(self, prop.key)
                if prop.key == "media_type":
                    if result[prop.key] == 0:
                        result[prop.key] = "image"
                    else:
                        result[prop.key] = "video"

        return result


class ImageDb(object):
    """
    name : file name
    path : relative path
    created : creation time of file
    loc : gps location string : "123.xxx,-23.xxx". latitude and longitude
    """

    # table = "image"

    def __init__(self, db):
        self.db = db

    def reset(self):
        try:
            session = self.db.Session()
            session.query(Image).delete()
            session.commit()
        finally:
            self.db.Session.remove()

    def put(self, name, path, created, media_type, ext, loc, flag):
        created_time = created
        # datetime(2017, 12, 5)
        image = Image(
            name=name,
            path=path,
            created=created_time,
            media_type=media_type,
            ext=ext,
            loc=loc,
            flag=flag,
        )

        session = self.db.Session()
        try:
            session.add(image)
            session.commit()
            log.info("image is added. %s", image)
        except exc.IntegrityError as e:
            session.rollback()
            d = {
                Image.created: image.created,
                Image.media_type: image.media_type,
                Image.ext: image.ext,
                Image.loc: image.loc,
                Image.flag: image.flag,
            }
            session.query(Image).filter(Image.path == path).update(d, False)
            session.commit()
        except Exception as e:
            log.info(e)
            session.rollback()
        finally:
            self.db.Session.remove()

    def to_media_value(self, str):
        r = []
        if str == "video":
            r.append(1)
        elif str == "image":
            r.append(0)
        else:
            r = [0, 1]

        return r

    def get_next_by_id(self, id, media_str, startDate, endDate):
        retry = 0

        endDate = endDate + " 23:59:59"

        media = self.to_media_value(media_str)
        while True:
            session = self.db.Session()
            try:
                """find image with id.  start <= created <= end"""
                image = (
                    session.query(Image)
                    .filter(Image.id == id)
                    .filter(and_(Image.created >= startDate, Image.created <= endDate))
                    .filter(Image.media_type.in_(media))
                    .first()
                )

                if image:
                    created = image.created
                    # find next one in the same date
                    image = (
                        session.query(Image)
                        .filter(and_(Image.id > id, Image.created == created))
                        .filter(Image.media_type.in_(media))
                        .order_by(Image.id)
                        .first()
                    )

                    if image:
                        return image.as_dict()
                    else:
                        # find next in the next day
                        image = (
                            session.query(Image)
                            .filter(created < Image.created)
                            .filter(
                                and_(
                                    Image.created >= startDate, Image.created <= endDate
                                )
                            )
                            .filter(Image.media_type.in_(media))
                            .order_by(Image.created, Image.id)
                            .first()
                        )

                        if image:
                            return image.as_dict()

                # fail to find next one in date range.
                # find the first one in date range
                image = (
                    session.query(Image)
                    .filter(and_(Image.created >= startDate, Image.created <= endDate))
                    .filter(Image.media_type.in_(media))
                    .order_by(Image.created, Image.id)
                    .first()
                )

                if image:
                    return image.as_dict()

                # no image in this range.  Now ignore date
                return get_next_by_id(id, media_str)

            except Exception as e:
                log.error("get_next_by_time Error.  %s", e)
                session.rollback()
                #                self.db.reset_session()
                retry += 1
                if retry > 3:
                    log.error("db operation failure. quit")
                    sys.exit(0)
            finally:
                self.db.Session.remove()

    def get_next_by_date(self, created, media_str, startDate, endDate):
        retry = 0

        endDate = endDate + " 23:59:59"
        media = self.to_media_value(media_str)
        while True:
            session = self.db.Session()
            try:
                image = (
                    session.query(Image)
                    .filter(Image.created >= created)
                    .order_by(Image.created, Image.id)
                    .first()
                )

                if image:
                    return image.as_dict()

                image = session.query(Image).order_by(Image.created, Image.id).first()

                return image.as_dict()
            except Exception as e:
                log.error("get_next_by_time Error.  %s", e)
                session.rollback()
                #                self.db.reset_session()
                retry += 1
                if retry > 3:
                    log.error("db operation failure. quit")
                    sys.exit(0)
            finally:
                self.db.Session.remove()

    def get_by_id(self, id, media_str, startDate, endDate):
        retry = 0

        endDate = endDate + " 23:59:59"
        media = self.to_media_value(media_str)
        while True:
            session = self.db.Session()
            try:
                """by time"""
                image = (
                    session.query(Image)
                    .filter(Image.id == id)
                    .filter(Image.media_type.in_(media))
                    .first()
                )

                if not image:
                    image = session.query(Image).filter(Image.id == id).first()

                    if not image:
                        image = (
                            session.query(Image)
                            .filter(Image.media_type.in_(media))
                            .order_by(Image.created)
                            .first()
                        )

                return image.as_dict()
            except Exception as e:
                log.error("get_next_by_time Error.  %s", e)
                session.rollback()
                #                self.db.reset_session()
                retry += 1
                if retry > 3:
                    log.error("db operation failure. quit")
                    sys.exit(0)
            finally:
                self.db.Session.remove()


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
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(name)s.%(funcName)s %(levelname)s %(message)s",
    )

    import image_builder
    from db import Db

    db = Db()
    imagedb = ImageDb(db)

    id = -1
    for i in xrange(20):
        image = imagedb.get_next_by_id(id, "both", "2017-10-12", "2017-10-14")
        print("+++++++++++++++++++++++++++++", image)
        id = image["id"]

"""
{'loc': u'37.350078,-121.981169', 
'path': u'media/1.jpg', 
'created': u'2015:10:03 01:31:01', 
'id': 1, 
'name': u'1.jpg'}

"""
