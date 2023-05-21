
import os
from flask import (
    Flask, render_template, request, redirect, g
)
from werkzeug.utils import secure_filename

from src.cv import ScreenShotAnalysis

cv = ScreenShotAnalysis()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['IMAGE_UPLOADS'] = 'static/images/'


@app.route("/home", methods=['GET', 'POST'])
def upload_image():
    if request.method == "POST":
        image = request.files['file']

        if image.filename == '':
            print("No file uploaded!")
            redirect(request.url)

        filename = secure_filename(image.filename)
        img_path = os.path.join(BASE_DIR, app.config['IMAGE_UPLOADS'], filename)
        image.save(img_path)
        g.filename = filename
        # text = cv.process(img_path)
        # return render_template("main.html", filename=filename, text=text)
        return render_template("dev2.html", filename=filename)

    return render_template("dev2.html")

# @app.route("/display/<filename>")
# def display_image(filename):
#     return redirect(url_for('static', filename='/images/'+filename), code=301)

# @app.route("/analyze/<filename>", methods=["GET, POST"])
# def analyze_image(filename):
@app.route("/analyze", methods=["GET", "POST"])
def analyze_image():
    # print(request)
    # print(request.url)
    # print(request.args)
    # print(request.args.get('filename'))

    # we already sanitized this when image was uploaded
    filename = request.args.get('filename')
    img_path = os.path.join(BASE_DIR, app.config['IMAGE_UPLOADS'], filename)
    text = cv.process(img_path)
    return render_template("dev2.html", filename=filename, text=text)
    # return render_template("dev2.html")

app.run(port=5000, debug=True)