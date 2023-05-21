
import os
from flask import Flask, render_template, request, redirect
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
        text = cv.process(img_path)
        return render_template("main.html", filename=filename, text=text)

    return render_template("main.html")

@app.route("/display/<filename>")
def display_image(filename):
    return redirect(url_for('static', filename='/images/'+filename), code=301)

app.run(port=5000, debug=True)