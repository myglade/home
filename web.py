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

import config
import datetime
import image_manager
import json
import logging
from logging.handlers import TimedRotatingFileHandler
import socket
import sys

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
    img = image_manager.get_newimage(id)

    img['path'] = "%s/%s" % (config.get("web_media_path"), 
                             img['path'].replace(os.path.sep, '/'))

    log.debug("oid=%s, id=%s", id, img['id'])

    created_time = img['created']

    # address transformation
    addr = img['address']
    addr_desc = ""
    if addr != "Not Found":
        t = addr.split(',')
        if len(addr) > 2:
            addr_desc = "%s,%s" % (t[1], t[2])
        else:
            addr_desc = addr

    if addr_desc:
        img['desc'] = config.get("desc_format") % (created_time, addr_desc)
    else:
        img['desc'] = created_time

    img['slide_delay'] = config.get("slide_delay")
    img['fade_delay'] = config.get("fade_delay")

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

    app.run(host= '0.0.0.0', port=port, threaded=True)


# http://192.168.1.10:5000/media/2009-1/SNC13009.jpg
