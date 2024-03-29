"""
GeoPy 

Package : https://pypi.python.org/pypi/geopy/
Documentation : http://geopy.readthedocs.io/en/latest/


Exif
Package : https://pypi.python.org/pypi/piexif

http://piexif.readthedocs.io/en/latest/sample.html#rotate-image-by-exif-orientation
 
"""

'''
https://www.scribd.com/doc/87043367/HandBrake-CLI-Guide


HandBrakeCLI.exe -vo -i {in} -o {out} --optimize --format mp4 --ab 64 --mixdown mono --quality 23 -e x264 -x vbv-bufsize=8000:vbv-maxrate=4000 --width 1280 --height 720

vbv-bufsize = 2 * vbv-maxrate

Youtube : in general, vbv-maxrate=5000

'''

import config
import datetime
from shutil import copyfile
import decimal
import logging
import os
import piexif
from PIL import Image
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from win32_setctime import setctime

log = logging.getLogger(config.logname)

# modify image
MODIFY_ROTATE=1
MODIFY_ROTATE_FAIL=2
NON_JPG=4

MEDIA_IMG = 0
MEDIA_VIDEO = 1

ENCODER = 'HandBrakeCLI.exe -i {in} -o {out} --optimize --format mp4 --ab 64 --mixdown mono --quality 23 -e x264 -x vbv-bufsize={bufsize}:vbv-maxrate={rate} --width 1280 --height 720'

class ImageBuilder(object):
    DEFAULT_SIZE = (1920, 1080)
    SMALL_SIZE = (1280, 720)
    THUMBNAIL = (320, 240)

    def __init__(self, video_rate=4000):
        self.image_path = config.get("image_path")

        if not os.path.exists(self.image_path):
            os.makedirs(self.image_path)

        self.rate = video_rate

        self.ext = ['jpg', 'gif', 'png', 'tiff', 'mp4', 'm4v', 'mov']
        self.image_type = ['jpg', 'gif', 'png', 'tiff']
        self.video_type = ['avi', 'm2ts', 'mp4', 'mov']

        self.video_overwrite = config.get("video_overwrite")
        self.db = None

    def get_info(self, name, ext):
        date = None
        loc = None
    
        if ext not in ["tiff", "jpg"]:
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

        if isinstance(date, (bytes, bytearray)):
            date = date.decode('utf-8')

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
        try:
            if "exif" in img.info:
                exif_dict = piexif.load(img.info["exif"])
                exif_bytes = piexif.dump(exif_dict)
        except Exception as e:
            log.warning("Fail to get exif.  e=%s, src=%s, dst=%s", e, src, dst)

        width = img.size[0]
        height = img.size[1]

        if img.size == size or (width <= size[0] or height <= size[1]):
            copyfile(src, dst)
            log.debug("file size is already small.  Just copy.  size=%s %s => %s",
                      size, src, dst)
            return

        if width >= height:
            w = size[0]
            h = (w * height) / width
        else:
            h = size[1]
            w = (width * h) / height

        img = img.resize((int(w), int(h)), Image.ANTIALIAS)
        
        try:
            if exif_bytes:
                img.save(dst, exif=exif_bytes) 
            else:
                img.save(dst)
        except Exception as e:
            log.error("Fail to resize %s.  e=%s", src, e.message)

        log.debug("file is resized to %s.  %s => %s",
                  size, src, dst)

    def convert_image(self, src, name, ext, stinfo):
        log.info("start convert image. src=%s, name=%s, ext=%s",
                 src, name, ext)
        loc = None

        d = datetime.datetime.fromtimestamp(stinfo.st_mtime)
        created_date = ""
        try:
            created_date, loc = self.get_info(src, ext)
            if created_date:
                d = datetime.datetime.strptime(created_date, "%Y:%m:%d %H:%M:%S")
            print(created_date)
        except Exception as e:
            log.warn("fail to getinfo e=%s, src=%s", e, src)
        
        if not created_date:
            t = src.split("\\")[-2]
            t1 = t.split("-")[0]
            created_date = f"{t1}:12:31 00:00:00"
            d = datetime.datetime.strptime(created_date, "%Y:%m:%d %H:%M:%S")

        modify_flag = 0
        try:
            self.rotate_jpeg(src)

            if self.is_rotate:
                modify_flag += MODIFY_ROTATE
                # set original timestamp to rotated one
                os.utime(src, (stinfo.st_atime, stinfo.st_mtime))
        except Exception as e:
            log.error("Fail to adjust rotation %s. e-%s", src, e)
            modify_flag += MODIFY_ROTATE_FAIL

        t = created_date
        for i in range(len(created_date)):
            if created_date[i] == ' ':
                t = created_date[:i]
                break

        temp = None
        if t.find(':') != -1:
            temp = t.split(':')
        elif t.find('.') != -1:
            temp = t.split('.')
        elif t.find('/') != -1:
            temp = t.split('/')

        if not temp: # or year != temp[0]:     
            d = datetime.datetime.fromtimestamp(stinfo.st_mtime)
            year = d.strftime('%Y')
            mon = d.strftime('%m')
            log.warn("year : %s <> picture info : %s", year, temp[0])
        else:
            year = temp[0]
            mon = temp[1]

        rel_path =  os.path.join(year, mon)
        dst_path = os.path.join(self.image_path, rel_path)

        # resize to default 
        if not os.path.exists(dst_path):
            os.makedirs(dst_path)

        filename = name + "." + ext
        dst = os.path.join(dst_path, filename)
        self.resize(src, self.DEFAULT_SIZE, dst)
        setctime(dst, d.timestamp())
        os.utime(dst, (d.timestamp(), d.timestamp()))


        '''
        # resize to small
        path = os.path.join(dst_path, str(self.SMALL_SIZE[0]))
        if not os.path.exists(path):
            os.makedirs(path)

        dst = os.path.join(path, filename)
        self.resize(src, self.SMALL_SIZE, dst)
        os.utime(dst, (stinfo.st_atime, stinfo.st_mtime))

        # resize to thumbnail
        path = os.path.join(dst_path, str(self.THUMBNAIL[0]))
        if not os.path.exists(path):
            os.makedirs(path)

        dst = os.path.join(path, filename)
        self.resize(src, self.THUMBNAIL, dst)
        os.utime(dst, (stinfo.st_atime, stinfo.st_mtime))
        '''

        if self.db:
            self.db.put(filename, 
                        os.path.join(rel_path, filename), 
                        created_date,
                        MEDIA_IMG,
                        ext,
                        loc, 
                        modify_flag)

        log.info("end convert image. src=%s, name=%s, ext=%s",
                 src, name, ext)

    def convert_video(self, src, name, ext, stinfo):   
        log.info("start convert video. src=%s, name=%s, ext=%s",
                 src, name, ext)

        if ext == 'avi' or ext == 'm2ts':
            # if already converted to mp4, skip it
            temp = src + ".mp4"
            if os.path.exists(temp):
                log.info("%s already exists", temp)
                return

        year = ""
        mon = ""
        d = datetime.datetime.fromtimestamp(stinfo.st_mtime)
        # '- Creation date: 2020-03-22 19:35:43'

        tmp = ""
        if ext in ['m4v', 'mov', 'mp4']:
            parser = createParser(src)
            metadata = extractMetadata(parser)
            for line in metadata.exportPlaintext():
                if "- Creation date: " in line:
                    tmp = line[len("- Creation date: "):]
                    d = datetime.datetime.strptime(tmp, "%Y-%m-%d %H:%M:%S")
                    break

        if not tmp:
            t = src.split("\\")[-2]
            t1 = t.split("-")[0]
            d = datetime.datetime.strptime(f"{t1}:12:31 00:00:00", "%Y:%m:%d %H:%M:%S")

        year = d.strftime('%Y')
        mon = d.strftime('%m')
        rel_path = os.path.join(year, mon)
        dst_path = os.path.join(self.image_path, rel_path)
        if not os.path.exists(dst_path):
            os.makedirs(dst_path)

        dst = os.path.join(dst_path, name + ".mp4")

        if not os.path.exists(dst) or self.video_overwrite:
            input = { "in":src, 
                     "out":dst, 
                     "rate": self.rate, 
                     "bufsize":self.rate*2 }

            cmd = ENCODER.format(**input)

            log.debug(cmd) 
            log.debug("*******************************************************")
            r = os.system(cmd)
            log.debug("*******************************************************")
            if r != 0:
                log.error("Fail! convert video. src=%s, name=%s, ext=%s", 
                          src, name, ext)

                if os.path.exists(dst):
                    os.remove(dst)
                return

            log.info("convert: %s", dst)

        setctime(dst, d.timestamp())
        os.utime(dst, (d.timestamp(), d.timestamp()))
        
        if self.db:
            filename = name + ".mp4"
            self.db.put(filename, 
                        os.path.join(rel_path, filename), 
                        str(d),
                        MEDIA_VIDEO,
                        ext,
                        None, 
                        0)

        log.info("end convert video. src=%s, name=%s, ext=%s",
                 src, name, ext)

    def process(self, src, name, ext, media_type):
        stinfo = os.stat(src)

        try:
            if media_type == MEDIA_VIDEO:
                self.convert_video(src, name, ext, stinfo)
            else:
                self.convert_image(src, name, ext, stinfo)
        except Exception as e:
            log.error("error. e=%s. src=%s", e, src)
            print(e)

 

    def scan(self, scan_path):   
        log.info("start scan")

        for spath in scan_path:
            if not spath:
                continue
            for root, dirs, files in os.walk(spath):
                for file in files:
                    filename, ext = os.path.splitext(file)
                    ext = ext[1:].lower()
                    if ext not in self.ext:
                        continue

                    if ext in self.image_type:
                        media_type = MEDIA_IMG
                    else:
                        media_type = MEDIA_VIDEO

                    path = os.path.join(root, file)
                    self.process(path, filename, ext, media_type)

    def start(self, db, paths):
        self.db = db
        t = paths.split(";")
        scan_path = list(set(t))

        self.scan(scan_path)
        
image_builder = ImageBuilder()

def test():   
    scan_path = "d:\\images\\"

    import shutil
    for root, dirs, files in os.walk(scan_path):
        for dir in dirs:
            if dir in ["320", "1280"]:
                path = os.path.join(root, dir)
                print(path)
                shutil.rmtree(path)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)s.%(funcName)s %(levelname)s %(message)s')

   
   #test()
    b = ImageBuilder()
   # b.get_info("d:\\IMG_3756.heic", "jpg");
   # info.resize("C:\\Users\\heesung\\Desktop\\media\\1.JPG", (1920, 1080), 
   #             "C:\\Users\\heesung\\Desktop\\media\\1920\\1.JPG")
    #b = ImageBuilder()
    
    #b.process("e:\\temp\\2014-1\\IMG_20140101_0005.jpg","IMG_20140101_0005", "jpg", 0)
    b.process("D:\\Pictures\\2019-4\\IMG_1382.jpg","IMG_1382", "jpg", MEDIA_VIDEO)
    #b.process("y:\\Pictures\\2011-1\\IMG_0013.jpg","SNC13036", "jpg", 0)
    #b.process("y:\\Pictures\\2009-1\\SNC13036.jpg","SNC13036", "jpg", 0)
    #b.process("y:\\Pictures\\2008\\Diane_Erin 001-ANIMATION.gif","Diane_Erin 001-ANIMATION", "gif", 0)
    #b.start(None, "C:\\Users\\heesung\\Desktop\\media\\")


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

