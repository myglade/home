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
MODIFY_DATE=1
MODIFY_ROTATE=2
NON_JPG=4

class ImageInfo(object):
    def __init__(self, *args, **kwargs):
        self.prev_date = '2008.01.01  00:00:0'

        return super(ImageInfo, self).__init__(*args, **kwargs)

    def get(self, name):
        date = None
        loc = None
    
        _, ext = os.path.splitext(name)
        if ext not in [".tiff", ".jpg"]:
            raise Exception("Invalid extension. %s" % name)

        flag = 0
        try:
            self.rotate_jpeg(name)
        except Exception as e:
            log.error("Fail to adjust rotation %s. e-%s", name, e)
            raise e

        if self.is_rotate:
            flag += MODIFY_ROTATE

        exif_dict = piexif.load(name)
    
        if piexif.ExifIFD.DateTimeOriginal in exif_dict['Exif']:
            date = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal]
        elif piexif.ExifIFD.DateTimeDigitized in exif_dict['Exif']:
            date = exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized]
        else:
            log.warn("%s doesn't have date. infer from previous")
            date = self.prev_date
            flag += MODIFY_DATE

        self.prev_date = date

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

        return decimal.Decimal('%.6f' % v)

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
                    img = img.rotate(-90).transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 6:
                    img = img.rotate(-90)
                elif orientation == 7:
                    img = img.rotate(90).transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 8:
                    img = img.rotate(90)

                img.save(filename, exif=exif_bytes)

                self.is_rotate = True

image_info = ImageInfo()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)s.%(funcName)s %(levelname)s %(message)s')

    import gps_db
    import db

    gps = gps_db.GpsDb(db.Db())
    imageinfo = ImageInfo()
    _, loc, flag = imageinfo.get("y:\\Pictures\\2011-1\\SNC11083.jpg")
    addr = gps.get_location(loc)
    print addr
 #   get_img_info("/scratch/heuikim/Downloads/1.JPG")