from flask import Flask, render_template, request, jsonify
from detectors.fusion import analyze
from detectors.image_detector import extract_text_from_image

MAX_TEXT_CHARS = 5000
MAX_IMAGE_BYTES = 5 * 1024 * 1024

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.post("/api/check")
def check_text():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify(error="Paste a message, link or phone number first."), 400
    if len(text) > MAX_TEXT_CHARS:
        return jsonify(error="That message is too long. Keep it under 5000 characters."), 400
    return jsonify(analyze(text=text))


@app.post("/api/check-image")
def check_image():
    file = request.files.get("image")
    if not file:
        return jsonify(error="No image uploaded."), 400

    data = file.read(MAX_IMAGE_BYTES + 1)
    if len(data) > MAX_IMAGE_BYTES:
        return jsonify(error="Image is too large. Maximum size is 5 MB."), 413

    try:
        ocr_text = extract_text_from_image(data)
    except RuntimeError as exc:
        return jsonify(error=str(exc)), 500

    text = (request.form.get("text") or "").strip()
    return jsonify(analyze(text=text, image_text=ocr_text))


if __name__ == "__main__":
    app.run(debug=True)