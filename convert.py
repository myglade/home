import datetime
import os


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

if __name__ == "__main__":
    convert("Y:\\Pictures\\")