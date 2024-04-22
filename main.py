import os
from flask import Flask, request, jsonify
from helper import separate as separate_audio

app = Flask(__name__)

model = "htdemucs"
extensions = ["mp3", "wav", "ogg", "flac"]
two_stems = None

mp3 = True
mp3_rate = 320
float32 = False
int24 = False

in_path = '/tmp/uploads/demucs/tmp_in/'
out_path = '/tmp/uploads/demucs/separated/'

os.makedirs(in_path, exist_ok=True)
os.makedirs(out_path, exist_ok=True)

@app.route("/")
def hello_world():
    return jsonify({"message": "hello world"})

@app.route('/upload', methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    file_path = os.path.join(in_path, uploaded_file.filename)
    uploaded_file.save(file_path)

    return jsonify({"message": "File uploaded successfully", "file_path": file_path})

@app.route('/separate', methods=['GET'])
def separate():
    result = separate_audio(in_path, out_path)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))