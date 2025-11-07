import os
import subprocess
import uuid
import whisper

def transcribe_audio(url):
    # Unique base name for the output file
    base_name = f"audio_{uuid.uuid4().hex}"

    # yt-dlp command to extract audio in mp3 format
    command = [
        "yt-dlp",
        "-x",
        "--audio-format", "mp3",
        "-o", f"{base_name}.%(ext)s",   # ✅ This ensures real filename exists
        url
    ]

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # The output file will be something like: audio_<id>.mp3
    audio_file = f"{base_name}.mp3"

    if result.returncode != 0 or not os.path.exists(audio_file):
        print("yt-dlp error:", result.stderr.decode())
        raise RuntimeError("Failed to download audio")

    # Load Whisper
    model = whisper.load_model("base")
    result = model.transcribe(audio_file)

    # Cleanup
    os.remove(audio_file)

    return result["text"]