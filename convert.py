import config
import datetime
import logging
import os
from datetime import timedelta
import time

log = logging.getLogger(config.logname)

'''
https://www.scribd.com/doc/87043367/HandBrake-CLI-Guide


HandBrakeCLI.exe -vo -i {in} -o {out} --optimize --format mp4 --ab 64 --mixdown mono --quality 23 -e x264 -x vbv-bufsize=8000:vbv-maxrate=4000 --width 1280 --height 720

vbv-bufsize = 2 * vbv-maxrate

Youtube : in general, vbv-maxrate=5000

'''
ENCODER = 'HandBrakeCLI.exe -i {in} -o {out} --optimize --format mp4 --ab 64 --mixdown mono --quality 23 -e x264 -x vbv-bufsize={bufsize}:vbv-maxrate={rate} --width 1280 --height 720'

def convert(src, dst_path, rate=4000):   
    video_type = ['avi', 'm2ts', 'mp4', 'mov']

    filename, ext = os.path.splitext(src)
    ext = ext[1:].lower()
    if ext not in video_type:
        return

    stinfo = os.stat(src)
    origin_mtime = stinfo.st_mtime
    origin_atime = stinfo.st_atime

    if ext == 'avi' or ext == 'm2ts':
        # if already converted to mp4, skip it
        temp = filename + ".mp4"
        if os.path.exists(temp):
            log.info("%s already exists", temp)
            return

    filename, ext = os.path.splitext(os.path.basename(src))
    dst = os.path.join(dst_path, filename + ".mp4")

    input = { "in":src, "out":dst, "rate": rate, "bufsize":rate*2 }
    cmd = ENCODER.format(**input)
    print(cmd)
    log.debug(cmd) 
    log.debug("*******************************************************")
    r = os.system(cmd)
    log.debug("*******************************************************")
    if r != 0:
        log.error("FAIL!  %s", src)
        if os.path.exists(dst):
            os.remove(dst)
        return

    os.utime(dst, (origin_atime, origin_mtime))

    log.info("convert: %s", dst)

def fix(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            path = os.path.join(root, file)
            print("Check %s" % path)
            if not file.startswith("201"):
                print("error=", file)
                continue

            s = file
            year = int(file[:4])
            mon = int(file[4:6])
            day = int(file[6:8])
            hour = int(file[9:11])
            min = int(file[11:13])

            if mon >= 11 and day >= 5:
                hour_diff = 8
            else:
                hour_diff = 7

            dt = datetime.datetime(year, mon, day, hour, min)
            dt = dt - timedelta(hours=hour_diff)
            stinfo = os.stat(path)
            origin_mtime = stinfo.st_mtime
            origin_atime = stinfo.st_atime

            ts = time.mktime(dt.timetuple())
            os.utime(path, (origin_atime, ts))

    print("done")

if __name__ == "__main__":
    convert("C:\\Users\\heesung\\Desktop\\media\\IMG_8638.MOV",
            "C:\\Users\\heesung\\Desktop\\media\\movie")