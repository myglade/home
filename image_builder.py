"""
GeoPy 

Package : https://pypi.python.org/pypi/geopy/
Documentation : http://geopy.readthedocs.io/en/latest/


Exif
Package : https://pypi.python.org/pypi/piexif

http://piexif.readthedocs.io/en/latest/sample.html#rotate-image-by-exif-orientation
 
"""
import config
from shutil import copyfile
import decimal
import logging
import piexif
from PIL import Image
import os

import config

log = logging.getLogger(config.logname)

# modify image
MODIFY_ROTATE=1
MODIFY_ROTATE_FAIL=2
NON_JPG=4

class ImageInfo(object):
    def __init__(self, path=path, date=date, loc=loc, rotate_flag=rotate_flag):
        self.date = date
        self.loc = loc
        self.path = path
        self.rotate_flag = rotate_flag

class ImageBuilder(object):
    DEFAULT_SIZE = (1920, 1080)
    SMALL_SIZE = (1280, 720)
    THUMBNAIL = (320, 240)

    def __init__(self, *args, **kwargs):
        self.image_path = config.get("image_path")

        if not os.path.exists(self.image_path):
            os.makedirs(self.image_path)

    def get_info(self, name):
        date = None
        loc = None
    
        _, ext = os.path.splitext(name)
        if ext.lower() not in [".tiff", ".jpg"]:
            raise Exception("Not image file. %s" % name)

        exif_dict = piexif.load(name)
    
        if piexif.ExifIFD.DateTimeOriginal in exif_dict['Exif']:
            date = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal]
        elif piexif.ExifIFD.DateTimeDigitized in exif_dict['Exif']:
            date = exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized]

        gps = exif_dict['GPS']
        if gps:
            log.debug("piexif loc= %s %s, %s, %s", 
                      gps[piexif.GPSIFD.GPSLatitude], 
                      gps[piexif.GPSIFD.GPSLatitudeRef],
                      gps[piexif.GPSIFD.GPSLongitude], 
                      gps[piexif.GPSIFD.GPSLongitudeRef]);
    
            latitude = self.get_gps(gps[piexif.GPSIFD.GPSLatitude], gps[piexif.GPSIFD.GPSLatitudeRef])
            longitude = self.get_gps(gps[piexif.GPSIFD.GPSLongitude], gps[piexif.GPSIFD.GPSLongitudeRef])
    
            loc = str(latitude) + "," + str(longitude)

        return (date, loc)

    def gps_to_num(self, part):
        return float(part[0]) / float(part[1])

    def get_gps(self, coord, ref):
        count = len(coord)
        degrees = self.gps_to_num(coord[0]) if count > 0 else 0
        minutes = self.gps_to_num(coord[1]) if count > 1 else 0
        seconds = self.gps_to_num(coord[2]) if count > 2 else 0
    
        flip = -1 if ref == 'W' or ref == 'S' else 1
    
        v = float(flip) * (degrees + minutes / 60.0 + seconds / 3600.0)

        # doesn't need exact precision for gps.  3 floating point is enough
        return decimal.Decimal('%.3f' % v)
        #return decimal.Decimal('%.6f' % v)

    def rotate_jpeg(self, filename):
        img = Image.open(filename)
        self.is_rotate = False

        if "exif" in img.info:
            exif_dict = piexif.load(img.info["exif"])

            if piexif.ImageIFD.Orientation in exif_dict["0th"]:
                orientation = exif_dict["0th"].pop(piexif.ImageIFD.Orientation)
                if orientation == 1:
                    return

                exif_bytes = piexif.dump(exif_dict)

                if orientation == 2:
                    img = img.transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 3:
                    img = img.rotate(180)
                elif orientation == 4:
                    img = img.rotate(180).transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 5:
                    img = img.rotate(-90, expand=1).transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 6:
                    img = img.rotate(-90, expand=1)
                elif orientation == 7:
                    img = img.rotate(90, expand=1).transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 8:
                    img = img.rotate(90, expand=1)

                img.save(filename, exif=exif_bytes)

                self.is_rotate = True

    def resize(self, src, size, dst):
        img = Image.open(src)
          
        exif_bytes = None
        if "exif" in img.info:
            exif_dict = piexif.load(img.info["exif"])
            exif_bytes = piexif.dump(exif_dict)
        
        width = img.size[0]
        height = img.size[1]

        if img.size == size or (width < size[0] and height < size[1]):
            copyfile(filename, new_filename)
            log.debug("file size is already small.  Just copy.  size=%s %s => %s",
                      size, src, dst)
            return

        if width >= height:
            w = size[0]
            h = (w * height) / width
        else:
            h = size[1]
            w = (width * h) / height

        img = img.resize((w, h), Image.ANTIALIAS)
        
        try:
            img.save(dst, exif=exif_bytes) 
        except Exception as e:
            log.error("Fail to resize %s.  e=%s", src, e.message)

        log.debug("file is resized to %s.  %s => %s",
                  size, src, dst)

    def copy(self, src, dst_path, name):
        # resize to default 
        if not os.path.exists(dst_path):
            os.makedirs(dst_path)

        self.resize(src, self.DEFAULT_SIZE, os.path.join(dst_path, name))

        # resize to small
        path = os.path.join(dst_path, str(self.SMALL_SIZE[0]))
        if not os.path.exists(path):
            os.makedirs(path)

        self.resize(src, self.SMALL_SIZE, os.path.join(path, name))

        # resize to thumbnail
        path = os.path.join(dst_path, str(self.THUMBNAIL[0]))
        if not os.path.exists(path):
            os.makedirs(path)

        self.resize(src, self.THUMBNAIL, os.path.join(path, name))

    def process(self, src):
        flag = 0

        try:
            date, loc = self.get_info(src)
        except Exception as e:
            log.warn("%s", e)
         
        try:
            self.rotate_jpeg(src)
            if self.is_rotate:
                flag += MODIFY_ROTATE
        except Exception as e:
            log.error("Fail to adjust rotation %s. e-%s", src, e)
            flag += MODIFY_ROTATE_FAIL

        # make full dst path
        name = os.path.basename(src)
        temp = date.split(':')
        dst_path = os.path.join(self.image_path, temp[0], temp[1])

        self.copy(src, dst_path, name)

        return ImageInfo(dst_path, date, loc, flag)


image_builder = ImageBuilder()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)s.%(funcName)s %(levelname)s %(message)s')

   # info.resize("C:\\Users\\heesung\\Desktop\\media\\1.JPG", (1920, 1080), 
   #             "C:\\Users\\heesung\\Desktop\\media\\1920\\1.JPG")
    b = ImageBuilder()
    b.process("C:\\Users\\heesung\\Desktop\\media\\1.JPG")


'''
    import gps_db
    import db

    gps = gps_db.GpsDb(db.Db())
    imageinfo = ImageBuilder()
    _, loc, flag = imageinfo.get("y:\\Pictures\\2016-1\\IMG_2049.jpg")
    addr = gps.get_location(loc)
    print addr
 #   get_img_info("/scratch/heuikim/Downloads/1.JPG")
 '''

