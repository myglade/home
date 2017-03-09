import config
from gps_db import GpsDb
from image_db import ImageDb
import image_info
import logging
from media import Media, MediaObject
import os

'''
https://wiki.gnome.org/Projects/gexiv2
'''

log = logging.getLogger(__name__)

class ImageManager(object):
    def __init__(self, path=None):
        self.media = None
        self.imagedb = ImageDb(config.image_db)
        self.gpsdb = GpsDb(config.gps_db)

        if path:
            self.path = path
        else:
            self.path = config.image_path

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

    def reset_and_update_imagedb(self, restart_cron=False):
        if not self.path:
            log.error("path is not set")
            return

        self.imagedb.reset()
        self.stop()
        media = Media(self.path, "image")
        imagelist = media.scan()

        for value in imagelist.values():
            for name in value.file_path.keys():
                path = name
                break

            date, loc = image_info.image_info.get(path)
            self.imagedb.put(value.fullname(), path, date, loc)

        if restart_cron:
            self.start()

    def get_newimage(self, id):
       if not id:
           id = -1
       img = self.imagedb.get_next_by_time(id) 
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

def get_newimage(id):
    return image_mgr.get_newimage(id)

def reset_update_imagedb():
    return image_mgr.reset_and_update_imagedb()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)s.%(funcName)s %(levelname)s %(message)s')
    
    mgr = ImageManager("static\\media\\")
    mgr.reset_and_update_imagedb()
    print "done"