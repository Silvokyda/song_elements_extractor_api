import os

import subprocess

from flask import Flask, request, jsonify

app = Flask(__name__)

# subprocess.run(["python3", "-m", "pip", "install", "-U", "git+https://github.com/facebookresearch/demucs#egg=demucs"])

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

def find_files(in_path):
    out = []
    for file in os.listdir(in_path):
        if file.endswith(tuple(extensions)):
            out.append(os.path.join(in_path, file))
    return out

def separate_vocals(inp=None, outp=None):
    inp = inp or in_path
    outp = outp or out_path
    cmd = ["python3", "-m", "demucs.separate", "-o", str(outp), "-n", model]
    if mp3:
        cmd += ["--mp3", f"--mp3-bitrate={mp3_rate}"]
    if float32:
        cmd += ["--float32"]
    if int24:
        cmd += ["--int24"]
    if two_stems is not None:
        cmd += [f"--two-stems={two_stems}"]
    files = find_files(inp)
    if not files:
        return {"message": "No valid audio files in the provided directory"}
    process = subprocess.run(cmd + files, capture_output=True)
    if process.returncode != 0:
        return {"message": "Command failed, something went wrong."}
    else:
        return {"message": "Separation successful."}

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
    result = separate_vocals()
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))