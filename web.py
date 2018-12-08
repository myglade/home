from flask import (
    Flask, 
    request,
    jsonify,
    send_file,
    render_template,
    send_from_directory
    )
import os.path
import random

app = Flask(__name__, 
            static_folder='static', 
            static_url_path='',
            template_folder='static')

import image_manager
import datetime
import config
import json
import logging
from logging.handlers import TimedRotatingFileHandler
import socket
import sys
import weather

log = logging.getLogger(config.logname)

@app.route("/index.html")
def hello():
    return render_template('index.html', rand=random.randint(1, 10000000))

@app.route('/media/<path:path>')
def media_file(path):
    #dir = os.path.join(config.image_path, path)
    return send_from_directory(config.get("image_path"), path)

@app.route("/nextimage")
def next_image():
    id = request.args.get('id')
    start_date = request.args.get('date')
    media = request.args.get('media')
    cur_id = request.args.get('curid')
    quality = config.get("quality")

    if not request.remote_addr.startswith("192.168.") and \
        not request.remote_addr.startswith("127.0.0."):
        #log.info("not local network.  Disable video service")
        #media = "image"
        quality = config.get("quality_remote")

    if quality == 0:
        quality_str = "320/"
    elif quality == 1:
        quality_str = "1280/"
    else:
        quality_str = ""

    if id:
        img = image_manager.get_newimage(id, media)
    elif start_date:
        img = image_manager.get_newimage_by_date(start_date, media)
    elif cur_id:
        img = image_manager.get_newimage_by_curid(cur_id, media)

    img['path'] = "%s/%s" % (config.get("web_media_path"), 
                             img['path'].replace(os.path.sep, '/'))

    if img['media_type'] == 'image':
        s = img['path']
        i = s.rfind("/")
        img['path'] = s[:i+1] + quality_str + s[i+1:]
    
    log.debug("oid=%s, id=%s, start_date=%s, media=%s, ip=%s", 
              id, img['id'], start_date, media, request.remote_addr)

    created_time = img['created']

    # address transformation
    addr = img['address']
    addr_desc = ""
    if addr != "Not Found":
        t = addr.split(',')
        if len(t) > 2:
            addr_desc = "%s,%s" % (t[1], t[2])
        else:
            addr_desc = addr

    if addr_desc:
        img['desc'] = config.get("desc_format") % (created_time, addr_desc)
    else:
        img['desc'] = created_time

    img['slide_delay'] = config.get("slide_delay")
    img['fade_delay'] = config.get("fade_delay")

    weather.get_weather_info(img)

    s = jsonify(img)
    s.headers.add('Access-Control-Allow-Origin', '*')
    log.debug(s.data)
    return s

@app.route("/imagedb/<path:type>")
def imagedb(type):
    image_manager.process(type)
    return "success"

@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)

def is_port_used(port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        s.bind(("0.0.0.0", port))
    except socket.error as e:
        return True

    s.close()
    return False

if __name__ == "__main__":
    if not os.path.exists("log"):
        os.makedirs("log")
    logging.basicConfig(filename="log\\ss.log", level=logging.DEBUG,
                    format='%(asctime)s %(name)s.%(funcName)s %(levelname)s %(message)s')

    formatter = logging.Formatter('%(asctime)s %(name)s.%(funcName)s %(levelname)s %(message)s')

    fileHandler = TimedRotatingFileHandler("log\\%s.log" % config.logname,
                                            when="d",
                                            interval=1,
                                            backupCount=20)
    fileHandler.setFormatter(formatter)
    log.addHandler(fileHandler)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)
    log.addHandler(consoleHandler)

    port = 5000
    if is_port_used(port):
        log.error("port is being used.  Quit")
        sys.exit(0)

    weather.start(int(config.get("weather_update")))
    app.run(host= '0.0.0.0', port=port, threaded=True)


# http://192.168.1.10:5000/media/2009-1/SNC13009.jpg
