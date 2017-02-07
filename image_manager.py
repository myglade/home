from gps_db import GpsDb
from image_db import ImageDb
import logging
from media import Media, MediaObject

'''
https://wiki.gnome.org/Projects/gexiv2
'''

log = logging.getLogger(__name__)

IMAGE_DB = "image.sqlite"
GPS_DB = "gps_db"

class ImageManager(object):
    def __init__(self, *args, **kwargs):
        self.media = None
        self.imagedb = ImageDb(IMAGE_DB)
        self.gpsdb = GpsDb(GPS_DB)
        return super(ImageManager, self).__init__(*args, **kwargs)
        
    def start(self):
        if self.media:
            return

        self.media = Media(self.path, "image")
        self.media.start_cron(callback=self.scan_callback)

    def stop(self):
        if not self.media:
            return

        self.media.stop_cron()
        self.media = None

    def scan_callback(self, imagelist):
        newimages = self.get_newimages(imagelist)

        for image in newimages:
            prop = get_image_property(image)
            self.update_imagedb(image, prop)

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