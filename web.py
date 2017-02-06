from flask import Flask
app = Flask(__name__)

import image_manager
import json

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/nextimage")
def next_image():
    id = request.args.get('id')
    img = image_manager.get_newimage(id)
    str = json.dumps(your_data, ensure_ascii=False)

if __name__ == "__main__":
    app.run()