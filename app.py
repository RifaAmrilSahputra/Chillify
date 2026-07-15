from flask import Flask, jsonify, render_template, request, url_for
from roboflow import Roboflow
from collections import Counter
import os
import tempfile
from pathlib import Path
from uuid import uuid4

app = Flask(__name__)

def load_local_environment():
    """Muat konfigurasi dari .env tanpa menimpa environment sistem."""
    env_file = Path(__file__).with_name(".env")
    if not env_file.exists():
        return

    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_local_environment()

roboflow_api_key = os.getenv("ROBOFLOW_API_KEY")
if not roboflow_api_key:
    raise RuntimeError(
        "ROBOFLOW_API_KEY belum diatur. Salin .env.example menjadi .env, "
        "kemudian isi API key Roboflow Anda."
    )

rf = Roboflow(api_key=roboflow_api_key)
project = rf.workspace().project("penyakit-tanaman-cabai")
model = project.version(1).model


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/tentang")
def tentang():
    return render_template("tentang.html")


ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def analyze_image(image_file):
    """Jalankan prediksi dan kembalikan data hasil yang siap ditampilkan."""
    if not image_file or not image_file.filename:
        raise ValueError("Pilih file gambar terlebih dahulu.")

    extension = Path(image_file.filename).suffix.lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError("Gunakan gambar dengan format JPG, JPEG, atau PNG.")

    temp_file = tempfile.NamedTemporaryFile(suffix=extension, delete=False)
    temp_filename = temp_file.name
    temp_file.close()

    try:
        image_file.save(temp_filename)
        prediction_result = model.predict(temp_filename, confidence=50, overlap=30)

        results_directory = Path(app.static_folder) / "results"
        results_directory.mkdir(exist_ok=True)
        result_filename = f"hasil-{uuid4().hex}.jpg"
        prediction_result.save(str(results_directory / result_filename))
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

    predictions = prediction_result.json().get("predictions", [])
    class_counter = Counter(prediction["class"] for prediction in predictions)

    if class_counter:
        result_description = "Hasil pemantauan mendeteksi " + ", ".join(
            f"{count} {label}" for label, count in class_counter.items()
        ) + "."
    else:
        result_description = "Tidak ada objek yang terdeteksi pada gambar ini."

    return {
        "predictions": predictions,
        "result_image": url_for("static", filename=f"results/{result_filename}"),
        "result_description": result_description,
    }


@app.route("/api/deteksi", methods=["POST"])
def api_deteksi():
    try:
        result = analyze_image(request.files.get("file"))
        return jsonify(result)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except Exception:
        app.logger.exception("Deteksi gambar gagal diproses.")
        return jsonify({"error": "Gagal menganalisis gambar. Silakan coba lagi."}), 500


@app.route('/layanan', methods=['GET', 'POST'])
def layanan():
    if request.method == "POST":
        try:
            return render_template("layanan.html", **analyze_image(request.files.get("file")))
        except ValueError as error:
            return render_template("layanan.html", error_message=str(error))

    return render_template("layanan.html")


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
