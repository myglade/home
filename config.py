import json
import logging
import os

# don't make log or home_config variable

HOME_CONFIG="home.ini"
logname = "slideshow"
log = logging.getLogger("slideshow")

##########################################
## quality : 0, 1, 2 (high)

conf_data = {
    "image_db": "image.sqlite",
    "gps_db": "gps_db",
    "image_path": "d:\\images",
    "image_scan_path": "d:\\Pictures\temp",
    "web_media_path": "media",
    "slide_delay": 3000,
    "fade_delay": 50,
    "video_overwrite" : False,
    "desc_format": "%s&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + \
                   "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;%s",
    "quality": 2,
    "quality_remote": 1,
    "weather_update": 15
    }

##########################################
class Info(object):
    def __init__(self):
        self.last_mtime = 0
        self.conf_data = conf_data

info = Info()


def load(info):
    try:
        mtime = os.path.getmtime(HOME_CONFIG)
        if mtime == info.last_mtime:
            return

        with open(HOME_CONFIG) as f:
            d = json.load(f)

            t = info.conf_data.copy()
            t.update(d)
            info.conf_data = t
            info.last_mtime = mtime
    except Exception as e:
        log.error("error in reading %s, e=%s" % (HOME_CONFIG, e))
        # save default
        s = json.dumps(info.conf_data, indent=4, separators=(',', ': '))
        with open(HOME_CONFIG, 'w') as f:
                f.write("%s" % s)

def get(key):
    load(info)
    return info.conf_data[key]

if __name__ == "__main__":
    text = "hi , I'm text"
    bb = text.encode('utf-8')
    s = "aaaa"
    b = bb.decode("utf-8", "strict")
    print("bbb")
