import os
import json
import collections

class Media(object):
    def __init__(self, name, dir, file_path):
        self.name = name 
        self.dir = dir
        size = os.path.getsize(filename)
        self.file_path = OrderedDict({file_path : size})
        self.date = os.path.getmtime(file_path)

class MediaList(object):
    """description of class"""
    def __init__(self, dirlist, type):
        self.dirlist = dirlist
        if type == "video":
            self.ext = ['.mp4', '.avi', '.mkv', '.wmv', '.asf', '.mpg', 'm4v', 'mov']
        elif type == "audio":
            self.ext = ['.mp3']
        else:
            raise "Invalid type"

        self.media_list = {}

    def scan(self):   
        self.media_list = [] 
        for subdir, dirs, files in os.walk(unicode(self.dirlist)):
            for file in files:
                filename, ext = os.path.splitext(file)
                if ext not in self.ext:
                    continue

                file_path = os.path.join(subdir, file)
                if subdir == self.dirlist:
                    media = Media(filename, subdir, file_path)
                else:
                    path_list = subdir.split(os.sep)
                    media = Media(path_list[-1], subdir, file_path)
                    
                
                if media.name in self.media_list: 
                    self.media_list[media.name].file_path[file_path] = media.file_path[file_path]
                else:       
                    self.media_list[media.name] = media
       
        s = json.dumps([ob.__dict__ for ob in self.items], 
                       ensure_ascii=False, 
                       encoding='utf8', 
                       indent=4, 
                       separators=(',', ': ')) 
        print s

ol = MediaList("z:\\torrent\\__downloaded\\", "video")
ol.scan()
print "done"