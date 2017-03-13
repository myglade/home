import datetime
import json
from collections import OrderedDict
import logging
import os
from threading import Event, Thread
import time

import config

log = logging.getLogger(config.log)

class Image(object):
    def __init__(self, name, rel_path):
        self.name = name 
        self.rel_path = rel_path

class Imagelist(object):
    """description of class"""
    def __init__(self, seed_path):
        self.seed_path = seed_path
        self.ext = ['jpg', 'gif', 'png', 'tiff']
        
        if not self.seed_path.endswith(os.path.sep):
            self.seed_path += os.path.sep

        self.imagelist = []
        self.cron_callback = None

    def get_imagelist_as_json(self):
        json_str = json.dumps([ob.__dict__ for ob in self.imagelist.itervalues()], 
                       ensure_ascii=False, 
                       encoding='utf8', 
                       indent=4, 
                       separators=(',', ': ')) 
        json_str.replace("\\\\", "\\")

        return json_str

    def get_imagelist(self):
        return self.imagelist

    def start_cron(self, callback=None, interval=300):
        self.cron_callback = callback
        self.stopped = Event()
        def loop():
            while not self.stopped.wait(interval): # the first call is in `interval` secs
                self.scan()

        Thread(target=loop).start()  

    def stop_cron(self):
        self.stopped.set()

    def scan(self, callback):   
        log.info("start scan")

        self.imagelist = [] 
        for root, dirs, files in os.walk(unicode(self.seed_path)):
            for file in files:
                filename, ext = os.path.splitext(file)
                ext = ext[1:]
                if ext not in self.ext:
                    continue

                path = os.path.join(root, file)
                l = len(unicode(self.seed_path))
                rel_path = os.path.join(root[l:], file)
                callback(file, rel_path, path, ext)
                #self.imagelist.append(Image(file, rel_path))

        log.info("finish scan")
        if self.cron_callback:
            self.cron_callback(self.imagelist)

        return self.imagelist

