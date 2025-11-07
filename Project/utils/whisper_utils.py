from yt_dlp import YoutubeDL
import whisper
import os
import uuid
import torch

def transcribe_audio(url):
    base = f"audio_{uuid.uuid4().hex}"

    ydl_opts = {
        "format": "bestaudio/best",
        "cookiefile": "cookies.txt",
        "user_agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        },
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

    model = whisper.load_model("base", device="cuda")
    result = model.transcribe(audio_file)
    os.remove(audio_file)
    return result["text"]