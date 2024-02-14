
import os

from flask import (
    Flask, render_template, request, redirect, g
)
from werkzeug.utils import secure_filename

from src.cv import ScreenShotAnalysis


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
cv = ScreenShotAnalysis()
app = Flask(__name__)
app.config['IMAGE_UPLOADS'] = 'static/images/'
os.makedirs(os.path.join(BASE_DIR, app.config['IMAGE_UPLOADS']), exist_ok=True)


@app.route("/")
def index():
    return render_template("main.html")


@app.route("/upload", methods=['GET', 'POST'])
def upload_image():
    if request.method == "POST":
        image = request.files['file']

        if image.filename == '':
            print("No file uploaded!")
            redirect(request.url)

        filename = secure_filename(image.filename)
        print(filename)
        img_path = os.path.join(BASE_DIR, app.config['IMAGE_UPLOADS'], filename)
        image.save(img_path)
        g.filename = filename
        return render_template("main.html", filename=filename)

    return render_template("main.html")


@app.route("/analyze", methods=["GET", "POST"])
def analyze_image():
    # we already sanitized this when image was uploaded
    filename = request.args.get('filename')
    img_path = os.path.join(BASE_DIR, app.config['IMAGE_UPLOADS'], filename)
    # text = cv.process(img_path)
    num_words, word_list = cv.process(img_path)
    # TODO: handle num_words = 0 and word_list = []
    return render_template("main.html", filename=filename, text=num_words, 
                           word_list=word_list)


app.run(port=8080, debug=True)