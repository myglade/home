import config
import logging
import sqlite3

log = logging.getLogger(config.logname)

        # http://bytefish.de/blog/first_steps_with_sqlalchemy/
        # http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#querying

from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Db(object):
    def __init__(self):
        engine = create_engine('sqlite:///:memory:', echo=True)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

