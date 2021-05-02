import config
import datetime
import logging
import os
import time

from sqlalchemy.exc import InterfaceError

from db import Db
from gps_db import GpsDb
from image_db import ImageDb

'''
https://wiki.gnome.org/Projects/gexiv2
'''

log = logging.getLogger(config.logname)

class ImageManager(object):
    def __init__(self, path=None):
        self.media = None

        retry = 0
        while True:
            try:
                self.db = Db()
                break
            except InterfaceError as e:
                print("[%d] Retry.  %s" % (retry, e))
                time.sleep(5)

                retry += 1
                if retry > 100:
                    raise e

        self.imagedb = ImageDb(self.db)
        self.gpsdb = GpsDb(self.db)
        self.reset = False

        if path:
            self.path = path
        else:
            self.path = config.get("image_path")

        return super(ImageManager, self).__init__()
        
    def set_media_path(self, path):
        self.path = path

    def get_newimage(self, id, media, startDate, endDate):
       if not id:
           id = -1

       if self.reset:
           id = -1
           self.reset = False

       img = self.imagedb.get_next_by_id(id, media, startDate, endDate) 

       address = None
       try:
           address = self.gpsdb.get_location(img["loc"])
       except Exception as e:
           log.debug("In accessing api, exception.  \n%s", e)

       img["address"] = address

       return img


    def get_newimage_by_curid(self, id, media, start_date, end_date):
       if not id:
           return self.get_newimage(-1, media)

       img = self.imagedb.get_by_id(id, media, start_date, end_date) 

       address = None
       try:
           address = self.gpsdb.get_location(img["loc"])
       except Exception as e:
           log.debug("In accessing api, exception.  \n%s", e)

       img["address"] = address

       return img

    def get_newimage_by_date(self, set_date, media, start_date, end_date):
       if not start_date:
           return self.get_newimage(-1)

       img = self.imagedb.get_next_by_date(set_date, media, start_date, end_date) 

       address = None
       try:
           address = self.gpsdb.get_location(img["loc"])
       except Exception as e:
           log.debug("In accessing api, exception.  \n%s", e)

       img["address"] = address

       return img

    def build_imagedb(self, reset, restart_cron=False):
        import image_builder

        if not self.path:
            log.error("path is not set")
            return

        if reset:
            self.imagedb.reset()

        scan_path = config.get("image_scan_path")
        image_builder.image_builder.start(self.imagedb, scan_path)


image_mgr = ImageManager()

def get_newimage(id, media, start_date, end_date):
    return image_mgr.get_newimage(id, media, start_date, end_date)

def get_newimage_by_date(set_date, media, start_date, end_date):
    return image_mgr.get_newimage_by_date(set_date, media, start_date, end_date)

def get_newimage_by_curid(cur_id, media, start_date, end_date):
    return image_mgr.get_newimage_by_curid(cur_id, media, start_date, end_date)


def process(type):
    if type == "build":
        return image_mgr.build_imagedb(False)
    elif type == 'update':
        return image_mgr.build_imagedb(False)
    elif type == 'reset':
        image_mgr.reset = True


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)s.%(funcName)s %(levelname)s %(message)s')
    
    #mgr = ImageManager("static\\media\\")
    print("done")