import datetime
import json
from collections import OrderedDict
import logging
import os
from threading import Event, Thread
import time

import config

log = logging.getLogger(config.logname)

class MediaObject(object):
    def __init__(self, name, ext, dir, file_path):
        self.name = name 
        self.ext = ext
        self.dir = dir
        size = os.path.getsize(file_path)
        self.file_path = OrderedDict({file_path : size})
        self.date = str(datetime.datetime.fromtimestamp(os.path.getmtime(file_path)))
        
    def fullname(self):
        return "%s.%s" % (self.name, self.ext)

class Media(object):
    """description of class"""
    def __init__(self, dirlist, type):
        self.dirlist = dirlist
        if type == "video":
            self.ext = ['mp4', 'avi', 'mkv', 'wmv', 'asf', 'mpg', 'm4v', 'mov']
        elif type == "audio":
            self.ext = ['mp3']
        elif type == "image":
            self.ext = ['jpg', 'gif', 'png']
        else:
            raise "Invalid type"
        
        self.type = type
        self.media_list = {}
        self.cron_callback = None

    def get_media_list_as_json(self):
        json_str = json.dumps([ob.__dict__ for ob in self.media_list.itervalues()], 
                       ensure_ascii=False, 
                       encoding='utf8', 
                       indent=4, 
                       separators=(',', ': ')) 
        json_str.replace("\\\\", "\\")

        return json_str

    def get_media_list(self):
        return self.media_list

    def start_cron(self, callback=None, interval=300):
        self.cron_callback = callback
        self.stopped = Event()
        def loop():
            while not self.stopped.wait(interval): # the first call is in `interval` secs
                self.scan()

        Thread(target=loop).start()  

    def stop_cron(self):
        self.stopped.set()

    def scan(self):   
        log.info("start scan")

        self.media_list = {} 
        for subdir, dirs, files in os.walk(unicode(self.dirlist)):
            for file in files:
                filename, ext = os.path.splitext(file)
                ext = ext[1:]
                if ext not in self.ext:
                    continue

                file_path = os.path.join(subdir, file)
                if subdir == self.dirlist:
                    media = MediaObject(filename, ext, subdir, file_path)
                else:
                    path_list = subdir.split(os.sep)
                    media = MediaObject(path_list[-1], ext, subdir, file_path)
                
                if media.name in self.media_list: 
                    self.media_list[media.name].file_path[file_path] = media.file_path[file_path]
                else:       
                    self.media_list[media.name] = media

        log.info("finish scan")
        if self.cron_callback:
            self.cron_callback(self.media_list)

        return self.media_list

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)s.%(funcName)s %(levelname)s %(message)s')

#    ol = Media("y:\\torrent\\__downloaded\\", "video")
    ol = Media("y:\\\Pictures\\2015-2\\", "image")
    ol.start_cron(5)
    time.sleep(20)
    ol.stop_cron()
    log.info("done")


