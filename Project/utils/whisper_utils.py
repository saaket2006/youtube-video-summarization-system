import subprocess
import whisper
import os
import uuid

def transcribe_audio(url):
    # random filename to avoid conflicts
    audio_filename = f"audio_{uuid.uuid4().hex}.mp3"

    # Download audio using yt-dlp (never breaks, unlike pytube)
    command = [
        "yt-dlp",
        "-x", "--audio-format", "mp3",
        "-o", audio_filename,
        url
    ]
    subprocess.run(command, check=True)

    # Load Whisper & transcribe
    model = whisper.load_model("base")
    result = model.transcribe(audio_filename)

    # clean up
    os.remove(audio_filename)

    return result["text"]
