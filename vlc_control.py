import _winreg
import base64
import logging
import subprocess
import time
import urllib, urlparse
import urllib2

import config

"""
https://wiki.videolan.org/VLC_HTTP_requests/
"""


log = logging.getLogger(config.log)

def path2url(path):
    return urlparse.urljoin('file:', urllib.pathname2url(path))

def url2path(url):
    return urllib.url2pathname(urlparse.urlparse(url).path)


class Vlc(object):
    _password = "1234"
    _command_url = "http://%s:%d/requests/status.xml"
    _playlist_url = "http://%s:%d/requests/playlist.xml"

    def __init__(self, port, host="localhost", type="video"):
        key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, "Software\\VideoLAN\\VLC")
        # get (default) value
        self.app = _winreg.QueryValueEx(key, "")[0]

        # video or audio
        self.type = type
        self.host = host
        self.port = port
        self.pid = None

    def start(self):
        proc = subprocess.Popen([self.app, 
                                 '--http-port=%s' % (self.port)], 
                        stdout=subprocess.PIPE,
                        )
        self.pid = proc.pid

    def stop(self):
        pass

    def send(self, url):
        retry = 0
        while True:
            try:
                username = ""
                request = urllib2.Request(url)
                base64string = base64.encodestring('%s:%s' % (username, self._password)).replace('\n', '')
                request.add_header("Authorization", "Basic %s" % base64string)
                response = urllib2.urlopen(request)

#                response = urllib2.urlopen(url)
                break
            except urllib2.URLError as e:
                log.info(e)
                retry += 1
                if retry > 3:
                    raise e

                self.start()
                time.sleep(3)

        return response

    def status(self):
        status = self.send(self.status_url)
        log.debug(self.status_url)

    def playlist(self):
        response = self.send(self.playlist_url)

    def play(self, localfile):
        url = "%s?command=in_play&input=%s" % (self.command_url, path2url(localfile))
        response = self.send(url)

    def add_to_playlist(self, localfile):
        url = "%s?command=in_enqueue&input=%s" % (self.command_url, path2url(localfile))
        response = self.send(url)

    def delete_from_playlist(self, id):
        url = "%s?command=pl_delete&input=%s" % (self.command_url, id)
        response = self.send(url)

    def empty_playlist(self, id):
        url = "%s?command=pl_empty" % (self.command_url)
        response = self.send(url)

    def play_playlist(self, id=None):
        if id:
            url = "%s?command=pl_play&id=%s" % (self.command_url, id)
        else:
            url = "%s?command=pl_play" % (self.command_url)
        response = self.send(url)

    def toggle_pause(self, id=None):
        if id:
            url = "%s?command=pl_pause&id=%s" % (self.command_url, id)
        else:
            url = "%s?command=pl_pause" % (self.command_url)
        response = self.send(url)

    def stop(self):
        url = "%s?command=pl_stop" % (self.command_url)
        response = self.send(url)

    def next(self):
        url = "%s?command=pl_next" % (self.command_url)
        response = self.send(url)

    def prev(self):
        url = "%s?command=pl_previous" % (self.command_url)
        response = self.send(url)

    def sort(self, id, val):
        """
         If id=0 then items will be sorted in normal order, if id=1 they will be
             sorted in reverse order
             A non exhaustive list of sort modes:
               0 Id
               1 Name
               3 Author
               5 Random
               7 Track number
        """
        url = "%s?command=pl_sort&id=%d&val=%d" % (self.command_url, id, val)
        response = self.send(url)

    # toggle
    def loop(self):
        url = "%s?command=pl_loop" % (self.command_url)
        response = self.send(url)
    
    # toggle
    def repeat(self):
        url = "%s?command=pl_repeat" % (self.command_url)
        response = self.send(url)

    # toggle
    def fullscreen(self):
        url = "%s?command=fullscreen" % (self.command_url)
        response = self.send(url)

    def volume(self, inc):
        if inc > 0:
            url = "%s?command=volume&val=+%d" % (self.command_url, inc)
        elif inc < 0:
            url = "%s?command=volume&val=%d" % (self.command_url, inc)
        else:
            return

        response = self.send(url)

    def volume_abs(self, val):
        url = "%s?command=volume&val=%d" % (self.command_url, inc)
        response = self.send(url)

    @property
    def command_url(self):
        return self._command_url % (self.host, self.port)

    @property
    def status_url(self):
        return self._command_url % (self.host, self.port)

    @property
    def playlist_url(self):
        return self._playlist_url % (self.host, self.port)

class VlcController(object):
    def __init__(self, *args, **kwargs):
        key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, "Software\\VideoLAN\\VLC")
        # get (default) value
        value =  _winreg.QueryValueEx(key, "")
        print value

    def start(self):
        pass

    def stop(self):
        pass

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)s.%(funcName)s %(levelname)s %(message)s')

    con = VlcController()

    vlc = Vlc(8080)
    vlc.status()
    vlc.start()

    print "done"

