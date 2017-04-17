import config
from geopy.geocoders import Nominatim
from geopy.geocoders import GoogleV3
import logging

from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta
from sqlalchemy import Table, Column, Integer, String, DateTime, Index
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker, class_mapper, ColumnProperty

from db import Base

log = logging.getLogger(config.logname)

# erin
GOOGLE_API_1 = 'AIzaSyAaN2AdvaguOICezg-0igGuJrk1sz8GQ-A'

class Gps(Base):
    __tablename__ = "gps"
    __table_args__ = (Index('loc_index', "loc"), )

    id = Column(Integer, primary_key=True, autoincrement=True)
    loc = Column(String(128), unique=True)
    address = Column(String(512))

    def __repr__(self):
        return "<Gps (id=%d, loc='%s', address='%s')>" % \
                (self.id, self.loc, self.address)
    def as_dict(self):                                                                                                                                                                               
            result = {}                                                                                                                                                                                  
            for prop in class_mapper(self.__class__).iterate_properties:                                                                                                                                 
                if isinstance(prop, ColumnProperty):                                                                                                                                                     
                    result[prop.key] = getattr(self, prop.key)                                                                                                                                           
            return result

class GpsDb():
    table = 'gps'

    def __init__(self, db):
        self.db = db
        self.session = db.session
    
    def get(self, loc):
        row = self.session.query(Gps).filter(Gps.loc == loc).first()
        if not row:
            log.debug("key=%s not found", loc)
            return None

        log.debug("found.  %s", row)        
        return row.address
    
    def put(self, loc, address):
        gps = Gps(loc=loc, address=address)
        try:
            self.session.add(gps)
            self.session.commit()
        except Exception as e:
            log.info(e)
            self.session.rollback()

        log.debug("save %s, %s", loc, address)
        
    def get_location(self, loc):
        """
        loc (tuple) : geolocation.  latitude, longitude
        address (string): result address
        
        """
        if not loc:
            return "Not Found"

        log.debug("geo loc : %s", loc)
        address = self.get(loc)
        if address:
            log.debug("location is found at db. %s", address)
            return address
        
        log.debug("query Google Map")
        
        try:
            geolocator = GoogleV3(api_key=GOOGLE_API_1)
            location = geolocator.reverse(loc)
            if location: 
                address = location[0].address
                self.put(loc, address)
                log.debug("get address. %s : %s", loc, address)
                return address
        except Exception as e:
            log.debug("In accessing api, exception.  \n%s", e)

        log.info("api fails to get geo information")
 
        return "Not Found"
    