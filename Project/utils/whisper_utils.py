import os
import subprocess
import uuid
import whisper

def transcribe_audio(url):
    audio_filename = f"audio_{uuid.uuid4().hex}.mp3"

    # Download audio using yt-dlp
    command = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format", "mp3",
        "-o", audio_filename,
        url
    ]

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.returncode != 0:
        print("yt-dlp error output:", result.stderr.decode())
        raise RuntimeError("Failed to download audio")

    model = whisper.load_model("base")
    result = model.transcribe(audio_filename)

    # Clean up downloaded audio
    if os.path.exists(audio_filename):
        os.remove(audio_filename)

    return result["text"]