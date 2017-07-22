import config
import logging


log = logging.getLogger(config.logname)

        # http://bytefish.de/blog/first_steps_with_sqlalchemy/
        # http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#querying

from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

Base = declarative_base()

'''
dialect+driver://username:password@host:port/database

MySQL-Connector : Oracle mysql


'''

#MYSQL_URL="mysql+pymysql://root:root@127.0.0.1/home"
MYSQL_URL="mysql+mysqlconnector://root:root@127.0.0.1/home"

class Db(object):
    def __init__(self, db_url=None):
        if not db_url:
            db_url = MYSQL_URL

        # to display SQL, set echo = True
        engine = create_engine(db_url, echo=False, pool_recycle=3600, pool_size=100)
        Base.metadata.create_all(engine)
        session_factory = sessionmaker(bind=engine, expire_on_commit=False)
        self.Session = scoped_session(session_factory)
#        self.session = self.Session()

