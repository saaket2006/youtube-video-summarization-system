# whisper_utils.py
from yt_dlp import YoutubeDL
import whisper
import os
import uuid
import torch

# lazy import for ADKAdapter only when needed
def _translate_with_adk(text: str, target_language: str) -> str:
    try:
        from adk_adapter import ADKAdapter
    except Exception:
        from agents.adk_adapter import ADKAdapter

    adapter = ADKAdapter()
    prompt = (
        f"Translate the following text to {target_language}. "
        f"Preserve meaning and formatting.\n\n{text}"
    )
    return adapter.complete(prompt, temperature=0.0, max_tokens=4096)


def transcribe_audio(url: str, translate: bool = False, target_language: str = "en", model_size: str | None = None) -> str:

    # Hidden directory for audio files
    AUDIO_DIR = ".data/audio"
    os.makedirs(AUDIO_DIR, exist_ok=True)

    base = f"{AUDIO_DIR}/audio_{uuid.uuid4().hex}"

    ydl_opts = {
        "format": "bestaudio/best",
        "cookiefile": "cookies.txt",
        "outtmpl": f"{base}.%(ext)s",
        "user_agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ]
    }

    # Download audio
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    audio_file = f"{base}.mp3"

    if not os.path.exists(audio_file):
        raise RuntimeError("Audio download failed.")

    # Load Whisper model
    model_size = model_size or os.getenv("WHISPER_MODEL", "base")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = whisper.load_model(model_size, device=device)

    # Translation logic
    if translate and target_language.lower() in ("en", "english"):
        result = model.transcribe(audio_file, task="translate")
        text = result["text"]
    else:
        result = model.transcribe(audio_file)
        text = result["text"]

        if translate:
            text = _translate_with_adk(text, target_language)

    # Cleanup
    try: os.remove(audio_file)
    except: pass

    return text
