from flask import Flask, render_template, request
from roboflow import Roboflow
from collections import Counter
import os

app = Flask(__name__)

rf = Roboflow(api_key="nPES0FWRDsbOTHWjwhF5")
project = rf.workspace().project("penyakit-tanaman-cabai")
model = project.version(1).model


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/tentang")
def tentang():
    return render_template("tentang.html")


@app.route('/layanan', methods=['GET', 'POST'])
def layanan():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('layanan.html', error_message='No file part')

        image_file = request.files['file']

        temp_filename = 'temp.jpg'
        image_file.save(temp_filename)

        prediction_result = model.predict(temp_filename, confidence=50, overlap=30)
        result_image_path = "static/hasil.jpg"
        prediction_result.save(result_image_path)

        os.remove(temp_filename)

        response = prediction_result.json()

        predictions = response["predictions"]

        class_counter = Counter(pred['class'] for pred in predictions)
        result_data = [{'class': key, 'count': value} for key, value in class_counter.items()]

        result_description = "Hasil pemantauan adalah terdapat "
        result_description += ", ".join([f"{value} {key}" for key, value in class_counter.items()])

        return render_template('layanan.html', predictions=predictions, result_image=result_image_path,
                               result_description=result_description, error_message=None)

    return render_template('layanan.html', error_message=None)


@app.route("/kebun")
def kebun():
    return render_template("kebun.html")


@app.route("/tim")
def tim():
    return render_template("tim.html")


@app.route("/kontak")
def kontak():
    return render_template("kontak.html")


if __name__ == "__main__":
    app.run(debug=True)
