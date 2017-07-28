import datetime
import logging
import os
import time

from sqlalchemy.exc import InterfaceError

import config
from db import Db
from imagelist import Imagelist
from gps_db import GpsDb
from image_db import ImageDb
import image_info

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
                print "[%d] Retry.  %s" % (retry, e)
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
        
    def start(self, path=None):
        if self.media:
            return

        if path:
            self.path = path
        self.media = Media(self.path, "image")
        self.media.start_cron(callback=self.scan_callback)

    def stop(self):
        if not self.media:
            return

        self.media.stop_cron()
        self.media = None

    def set_media_path(self, path):
        self.path = path

    def scan_callback(self, imagelist):
        """ Not implemented yet """

        # get only new images. ie. exclude existing images of db
        newimages = self.get_newimages(imagelist)

        for image in newimages:
            prop = self.get_image_property(image)
            self.update_imagedb(image, prop)

    def build_imagedb(self, reset, restart_cron=False):
        def image_add(name, rel_path, path, ext, media_type):
            log.debug('scan %s', path)

            date = None
            loc = None
            modify_flag = 0

            stinfo = os.stat(path)
            origin_mtime = stinfo.st_mtime
            origin_atime = stinfo.st_atime

            try:
                date, loc, modify_flag = image_info.image_info.get(path)
            except Exception as e:
                log.warn("%s", e)

            stinfo = os.stat(path)
            if stinfo.st_mtime != origin_mtime:
                os.utime(path, (origin_atime, origin_mtime))
            
            # use modified data instead of taken date in exif 
            # exif date has many errors
            #if not date:
            date = str(datetime.datetime.fromtimestamp(origin_mtime))
                
            self.imagedb.put(name, rel_path, date, media_type, ext, loc, modify_flag)

        if not self.path:
            log.error("path is not set")
            return

        if reset:
            self.imagedb.reset()

        scan_path = config.get("image_scan_path")
        self.stop()
        imagelist = Imagelist(self.path, scan_path)
        images = imagelist.scan(image_add)

        if restart_cron:
            self.start()

    def get_newimage(self, id, media):
       if not id:
           id = -1

       if self.reset:
           id = -1
           self.reset = False

       img = self.imagedb.get_next_by_id(id, media) 
       img['created'] = img['created'].strftime("%Y / %m / %d")

       address = None
       try:
           address = self.gpsdb.get_location(img["loc"])
       except Exception as e:
           log.debug("In accessing api, exception.  \n%s", e)

       img["address"] = address

       return img

    def get_newimage_by_curid(self, id, media):
       if not id:
           return self.get_newimage(-1, media)

       img = self.imagedb.get_by_id(id, media) 
       img['created'] = img['created'].strftime("%Y / %m / %d")

       address = None
       try:
           address = self.gpsdb.get_location(img["loc"])
       except Exception as e:
           log.debug("In accessing api, exception.  \n%s", e)

       img["address"] = address

       return img

    def get_newimage_by_date(self, start_date, media):
       if not start_date:
           return self.get_newimage(-1)

       img = self.imagedb.get_next_by_date(start_date, media) 
       img['created'] = img['created'].strftime("%Y / %m / %d")

       address = None
       try:
           address = self.gpsdb.get_location(img["loc"])
       except Exception as e:
           log.debug("In accessing api, exception.  \n%s", e)

       img["address"] = address

       return img

    def update_imagedb(self, image, prop):
        pass

image_mgr = ImageManager()

def get_newimage(id, media):
    return image_mgr.get_newimage(id, media)

def get_newimage_by_date(start_date, media):
    return image_mgr.get_newimage_by_date(start_date, media)

def get_newimage_by_curid(cur_id, media):
    return image_mgr.get_newimage_by_curid(cur_id, media)

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
    
    mgr = ImageManager("static\\media\\")
    print "done"