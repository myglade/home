"""
GeoPy 

Package : https://pypi.python.org/pypi/geopy/
Documentation : http://geopy.readthedocs.io/en/latest/


Exif
Package : https://pypi.python.org/pypi/piexif

 
"""
import decimal
import logging
import piexif

from gps_db import GpsDb

log = logging.getLogger(__name__)

gps = GpsDb("gps.sqlite")

def get_img_info(name):
    date = None
    loc = None
    
    exif_dict = piexif.load(name)
    
    if piexif.ExifIFD.DateTimeOriginal in exif_dict['Exif']:
        date = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal]
    
    gps = exif_dict['GPS']
    if gps:
        log.debug("piexif loc= %s %s, %s, %s", 
                  gps[piexif.GPSIFD.GPSLatitude], 
                  gps[piexif.GPSIFD.GPSLatitudeRef],
                  gps[piexif.GPSIFD.GPSLongitude], 
                  gps[piexif.GPSIFD.GPSLongitudeRef]);
    
        latitude = get_gps(gps[piexif.GPSIFD.GPSLatitude], gps[piexif.GPSIFD.GPSLatitudeRef])
        longitude = get_gps(gps[piexif.GPSIFD.GPSLongitude], gps[piexif.GPSIFD.GPSLongitudeRef])
    
        loc = str(latitude) + "," + str(longitude)
   
    return (date, loc)


def gps_to_num(part):
    return float(part[0]) / float(part[1])

def get_gps(coord, ref):
    count = len(coord)
    degrees = gps_to_num(coord[0]) if count > 0 else 0
    minutes = gps_to_num(coord[1]) if count > 1 else 0
    seconds = gps_to_num(coord[2]) if count > 2 else 0
    
    flip = -1 if ref == 'W' or ref == 'S' else 1
    
    v = float(flip) * (degrees + minutes / 60.0 + seconds / 3600.0)

    return decimal.Decimal('%.6f' % v)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)s.%(funcName)s %(levelname)s %(message)s')

    get_img_info("media/1.jpg")
 #   get_img_info("/scratch/heuikim/Downloads/1.JPG")