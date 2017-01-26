import logging
from geopy.geocoders import Nominatim
from geopy.geocoders import GoogleV3
import decimal

from db import Db
from _sqlite3 import Row

log = logging.getLogger(__name__)

# erin
GOOGLE_API_1 = 'AIzaSyAaN2AdvaguOICezg-0igGuJrk1sz8GQ-A'


class GpsDb(Db):
    table = 'gps'

    def __init__(self, db_file):
        super(GpsDb, self).__init__(db_file)

        self.execute('''CREATE TABLE IF NOT EXISTS %s(
                            id      INTEGER PRIMARY KEY AUTOINCREMENT,
                            loc     TEXT,
                            address TEXT
                        );
                        ''' % self.table)

        self.execute("CREATE INDEX IF NOT EXISTS loc_index on %s(loc)" % self.table)
    
    def get(self, loc):
        self.execute("SELECT * FROM %s WHERE loc=?" % self.table, (loc,))
        row = self.cursor.fetchone()
        if not row:
            log.debug("key=%s not found", loc)
            return None

        log.debug("found.  %s", row)        
        return row["address"]
    
    def put(self, loc, address):
        self.execute("INSERT INTO %s(loc, address) VALUES(?,?)" % self.table, 
                            (loc, address))
        self.commit()
        log.debug("save %s, %s", loc, address)
        
    def get_location(self, loc):
        """
        loc (tuple) : geolocation.  latitude, longitude
        address (string): result address
        
        """
        latitude = decimal.Decimal('%.6f' % loc[0])
        longitude = decimal.Decimal('%.6f' % loc[1])
        key = str(latitude) + "," + str(longitude)
        log.debug("geo key : %s", key)
        
        address = self.get(key)
        if address:
            log.debug("location is found at db. %s", address)
            return address
        
        log.debug("query Google Map")
        
        try:
            geolocator = GoogleV3(api_key=GOOGLE_API_1)
            location = geolocator.reverse(key)
            if location: 
                address = location[0].address
                self.put(key, address)
                log.debug("get address. %s : %s", key, address)
                return address
        except Exception as e:
            log.debug("In accessing api, exception.  \n%s", e)

        log.info("api fails to get geo information")
        return "Not Found"
        
        return address
    