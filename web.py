from flask import (
    Flask, 
    request,
    jsonify,
    send_file,
    render_template
    )
import os.path
import random

app = Flask(__name__, 
            static_folder='static', 
            static_url_path='',
            template_folder='static')

import image_manager
import json
import logging

@app.route("/index.html")
def hello():
    return render_template('index.html', rand=random.randint(1, 10000000))

@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)

@app.route("/nextimage")
def next_image():
    id = request.args.get('id')
    img = image_manager.get_newimage(id)
    return jsonify(img)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)s.%(funcName)s %(levelname)s %(message)s')

    app.run()
