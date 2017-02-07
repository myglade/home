from flask import (
    Flask, 
    request,
    jsonify
    )

app = Flask(__name__)

import image_manager
import json
import logging

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/nextimage")
def next_image():

    a = request.args
    id = request.args.get('id')
    img = image_manager.get_newimage(id)
    return jsonify(img)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)s.%(funcName)s %(levelname)s %(message)s')

    app.run()