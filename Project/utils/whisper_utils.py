# whisper_utils.py
from yt_dlp import YoutubeDL
import whisper
import os
import uuid
import torch

# lazy import for ADKAdapter only when needed to avoid import cycles
def _translate_with_adk(text: str, target_language: str) -> str:
    try:
        from adk_adapter import ADKAdapter
    except Exception:
        # ADKAdapter might be in project root; try relative import
        from agents.adk_adapter import ADKAdapter  # fallback (if you put it in agents)
    adapter = ADKAdapter()
    prompt = (
        f"Translate the following text to {target_language}. Keep formatting and meaning intact.\n\n"
        f"TEXT:\n{text}"
    )
    return adapter.complete(prompt, temperature=0.0, max_tokens=4096)


def transcribe_audio(url: str, translate: bool = False, target_language: str = "en", model_size: str | None = None) -> str:
    
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

    # choose model size
    model_size = model_size or os.getenv("WHISPER_MODEL", "base")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = whisper.load_model(model_size, device=device)

    # If target language is English and translate requested, Whisper can translate directly
    if translate and (str(target_language).lower() in ("en", "english")):
        result = model.transcribe(audio_file, task="translate")
        text = result["text"]
    else:
        # First, transcribe (auto-detect language)
        result = model.transcribe(audio_file)
        text = result["text"]
        detected_lang = result.get("language", None)

        # If translation requested to non-English target, use ADK/Gemini to translate
        if translate:
            # If target_language is English but not recognized as 'en' string, handle anyway:
            text = _translate_with_adk(text, target_language)

    # cleanup
    try:
        os.remove(audio_file)
    except Exception:
        pass

    return text
