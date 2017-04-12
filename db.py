import config
import logging


log = logging.getLogger(config.logname)

        # http://bytefish.de/blog/first_steps_with_sqlalchemy/
        # http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#querying

from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

'''
dialect+driver://username:password@host:port/database


'''

MYSQL_URL="mysql+pymysql://root:root@127.0.0.1/home"

class Db(object):
    def __init__(self, db_url=None):
        if not db_url:
            db_url = MYSQL_URL

        engine = create_engine(db_url, echo=True)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

