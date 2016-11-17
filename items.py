import os
import json

class Item(object):
    def __init__(self, name, dir, filename):
        self.name = name 
        self.dir = dir
        self.filename = [filename]

class ObjectList(object):
    """description of class"""
    def __init__(self, dirlist, type):
        self.dirlist = dirlist
        if type == "video":
            self.ext = ['.mp4', '.avi', '.mkv', '.wmv', '.asf', '.mpg', 'm4v', 'mov']
        elif type == "audio":
            self.ext = ['.mp3']
        else:
            raise "Invalid type"

        self.items = {}

    def scan(self):   
        self.items = [] 
        for subdir, dirs, files in os.walk(unicode(self.dirlist)):
            for file in files:
                filename, ext = os.path.splitext(file)
                if ext not in self.ext:
                    continue

                if subdir == self.dirlist:
                    item = Item(filename, subdir, os.path.join(subdir, file))
                else:
                    path_list = subdir.split(os.sep)
                    item = Item(path_list[-1], subdir, os.path.join(subdir, file))
                    
                        
                self.items.append(item)
       
        s = json.dumps([ob.__dict__ for ob in self.items], 
                       ensure_ascii=False, 
                       encoding='utf8', 
                       indent=4, 
                       separators=(',', ': ')) 
        print s

ol = ObjectList("z:\\torrent\\__downloaded\\", "video")
ol.scan()
print "done"