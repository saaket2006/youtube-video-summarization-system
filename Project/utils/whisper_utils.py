from yt_dlp import YoutubeDL
import whisper
import os
import uuid

def transcribe_audio(url):
    base = f"audio_{uuid.uuid4().hex}"

    ydl_opts = {
        "format": "bestaudio/best",
        "cookiefile": "cookies.txt",   # ✅ add this
        "outtmpl": f"{base}.%(ext)s",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ]
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    audio_file = f"{base}.mp3"

    if not os.path.exists(audio_file):
        raise RuntimeError("Audio download failed.")

    model = whisper.load_model("base")
    result = model.transcribe(audio_file)
    os.remove(audio_file)
    return result["text"]