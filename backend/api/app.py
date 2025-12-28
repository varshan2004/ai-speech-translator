import os, uuid, json, tempfile
from flask import Flask, request, send_file, render_template, Response
from backend.pipeline.speech_pipeline import SpeechPipeline
from backend.services.video.youtube_service import download_youtube_audio

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "temp_uploads")
AUDIO_DIR = os.path.join(BASE_DIR, "temp_audio")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

app = Flask(
    __name__,
    static_folder="../static",
    template_folder="../templates"
)

pipeline = SpeechPipeline()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/translate/audio", methods=["POST"])
def translate_audio():
    file = request.files["file"]
    lang = request.form.get("target_lang", "ta")

    path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
    file.save(path)

    result = pipeline.process_audio(path, lang)
    return Response(json.dumps(result, ensure_ascii=False),
                    content_type="application/json")

@app.route("/api/translate/mic", methods=["POST"])
def translate_mic():
    audio = request.files["audio"]
    lang = request.form.get("target_lang", "ta")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav", dir=UPLOAD_DIR) as f:
        audio.save(f.name)
        path = f.name

    result = pipeline.process_audio(path, lang)
    return Response(json.dumps(result, ensure_ascii=False),
                    content_type="application/json")

@app.route("/api/translate/url", methods=["POST"])
def translate_url():
    data = request.get_json()
    url = data.get("url")
    lang = data.get("target_lang", "ta")

    if not url:
        return {"error": "URL missing"}, 400

    audio_path = download_youtube_audio(url, UPLOAD_DIR)
    result = pipeline.process_audio(audio_path, lang)

    return Response(json.dumps(result, ensure_ascii=False),
                    content_type="application/json")

@app.route("/api/audio/<filename>")
def serve_audio(filename):
    return send_file(os.path.join(AUDIO_DIR, filename),
                     mimetype="audio/mpeg")

if __name__ == "__main__":
    app.run(debug=True, port=8000)
