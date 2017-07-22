import datetime
import os
from datetime import timedelta
import time

def convert(path):   
    video_type = ['avi', 'm2ts']
    for root, dirs, files in os.walk(unicode(path)):
        for file in files:
            filename, ext = os.path.splitext(file)
            ext = ext[1:].lower()
            if ext not in video_type:
                continue

            path = os.path.join(root, file)
            print "Check %s" % path
            stinfo = os.stat(path)
            origin_mtime = stinfo.st_mtime
            origin_atime = stinfo.st_atime

            output = path + ".mp4"
            if os.path.exists(output):
                print "%s already exists" % output
                continue

            cmd = "HandBrakeCLI.exe -i \"%s\" -o \"%s\"" % (path, output)
            print cmd 
            print "*******************************************************"
            r = os.system(cmd)
            print "*******************************************************"
            if r != 0:
                print "FAIL!!!!!!!!!!!!!!!!!!!!!!    %s" % path
                os.remove(output)
                continue

            os.utime(output, (origin_atime, origin_mtime))

    print "done"

def fix(path):
    for root, dirs, files in os.walk(unicode(path)):
        for file in files:
            path = os.path.join(root, file)
            print "Check %s" % path
            if not file.startswith("201"):
                print "error=", file
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

    print "done"

if __name__ == "__main__":
    fix("Y:\\Pictures\\jin\\")