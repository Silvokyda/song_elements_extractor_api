import io
from pathlib import Path
import subprocess as sp
import select
import sys
import os
from typing import Dict, Tuple, Optional, IO
import demucs.separate

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
    for file in Path(in_path).iterdir():
        if file.suffix.lower().lstrip(".") in extensions:
            out.append(file)
    return out

def copy_process_streams(process: sp.Popen):
    def raw(stream: Optional[IO[bytes]]) -> IO[bytes]:
        assert stream is not None
        if isinstance(stream, io.BufferedIOBase):
            stream = stream.raw
        return stream

    p_stdout, p_stderr = raw(process.stdout), raw(process.stderr)
    stream_by_fd: Dict[int, Tuple[IO[bytes], io.StringIO, IO[str]]] = {
        p_stdout.fileno(): (p_stdout, sys.stdout),
        p_stderr.fileno(): (p_stderr, sys.stderr),
    }
    fds = list(stream_by_fd.keys())

    while fds:
        ready, _, _ = select.select(fds, [], [])
        for fd in ready:
            p_stream, std = stream_by_fd[fd]
            raw_buf = p_stream.read(2 ** 16)
            if not raw_buf:
                fds.remove(fd)
                continue
            buf = raw_buf.decode()
            std.write(buf)
            std.flush()
            
def separate(inp=None, outp=None):
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
    files = [str(f) for f in find_files(inp)]
    if not files:
        print(f"No valid audio files in {in_path}")
        return
    print("Going to separate the files:")
    print('\n'.join(files))
    print("With command: ", " ".join(cmd))
    p = sp.Popen(cmd + files, stdout=sp.PIPE, stderr=sp.PIPE)
    p.wait()
    if p.returncode != 0:
        return {"message": "Command failed, something went wrong."}
    else:
        separated_files = [os.path.join(outp, f"{file.stem}_vocals{file.suffix}") for file in files]
        return {"message": "Separation successful.", "separated_files": separated_files}

def from_upload():
    in_path = '/tmp/uploads/demucs/tmp_in/'
    out_path = '/tmp/uploads/demucs/separated/'

    if not os.path.exists(in_path):
        os.makedirs(in_path)

    if not os.path.exists(out_path):
        os.makedirs(out_path)

    uploaded_files = request.files.getlist("file")
    for uploaded_file in uploaded_files:
        filename = uploaded_file.filename
        file_path = os.path.join(in_path, filename)
        uploaded_file.save(file_path)
    separate(in_path, out_path)