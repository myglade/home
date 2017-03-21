import config
import logging
import sqlite3

from sqlalchemy import create_engine

log = logging.getLogger(config.logname)

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
            self.conn = sqlite3.connect(db_file, check_same_thread=False)
            
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


        # http://bytefish.de/blog/first_steps_with_sqlalchemy/

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from datetime import datetime, timedelta
from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref

class Image(Base):
    __tablename__ = "image"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    path = Column(String(512), nullable=False)
    created = Column(DateTime, nullable=False)
    loc = Column(String(128))

    def __repr__(self):
        created = self.created.strftime("%Y-%m-%d %H:%M:%S")
        return "<Image (id=%d, name='%s', path='%s', created='%s', loc='%s')>" % \
                (self.id, self.name, self.path, created, self.loc)

class Gps(Base):
    __tablename__ = "gps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    loc = Column(String(128))
    address = Column(String(512))

    def __repr__(self):
        return "<Gps (id=%d, loc='%s', address='%s')>" % \
                (self.id, self.loc, self.address)


engine = create_engine('sqlite:///:memory:', echo=True)
Base.metadata.create_all(engine)