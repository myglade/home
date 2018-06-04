"""
GeoPy 

Package : https://pypi.python.org/pypi/geopy/
Documentation : http://geopy.readthedocs.io/en/latest/


Exif
Package : https://pypi.python.org/pypi/piexif

http://piexif.readthedocs.io/en/latest/sample.html#rotate-image-by-exif-orientation
 
"""
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
    def __init__(self, *args, **kwargs):
        return super(ImageInfo, self).__init__(*args, **kwargs)

    def get(self, name):
        date = None
        loc = None
    
        _, ext = os.path.splitext(name)
        if ext.lower() not in [".tiff", ".jpg"]:
            raise Exception("Not image file. %s" % name)

        flag = 0
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
 
        try:
            self.rotate_jpeg(name)
            if self.is_rotate:
                flag += MODIFY_ROTATE
        except Exception as e:
            log.error("Fail to adjust rotation %s. e-%s", name, e)
            flag += MODIFY_ROTATE_FAIL

        return (date, loc, flag)

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

    def resize(self, filename, size, new_filename):
        self.rotate_jpeg(filename)
        img = Image.open(filename)
        
        exif_bytes = None
        if "exif" in img.info:
            exif_dict = piexif.load(img.info["exif"])
            exif_bytes = piexif.dump(exif_dict)
        
        width = img.size[0]
        height = img.size[1]

        if img.size == size or (width < size[0] and height < size[1]):
            return

        if width >= height:
            w = size[0]
            h = (w * height) / width
        else:
            h = size[1]
            w = (width * h) / height

        img = img.resize((w, h), Image.ANTIALIAS)
        
        try:
            img.save(new_filename, exif=exif_bytes) 
        except Exception as e:
            print e

image_info = ImageInfo()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)s.%(funcName)s %(levelname)s %(message)s')

    info = ImageInfo()
    info.resize("C:\Users\heesung\Desktop\New folder\IMG_7797.JPG", (1920, 1080), 
                "C:\\Users\\heesung\\Desktop\\New folder\\IMG_7797_1.JPG")


'''
    import gps_db
    import db

    gps = gps_db.GpsDb(db.Db())
    imageinfo = ImageInfo()
    _, loc, flag = imageinfo.get("y:\\Pictures\\2016-1\\IMG_2049.jpg")
    addr = gps.get_location(loc)
    print addr
 #   get_img_info("/scratch/heuikim/Downloads/1.JPG")
 '''

