# transcript_utils.py
import subprocess
import os
import uuid

def extract_video_id(url):
    if "v=" in url:
        return url.split("v=")[-1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[-1].split("?")[0]
    return None


def load_youtube_transcript(video_id, lang: str | None = None):

    # Unique filename
    base = f"sub_{uuid.uuid4().hex}"
    subtitle_file = base + ".vtt"

    # build the command
    command = [
        "yt-dlp",
        f"https://www.youtube.com/watch?v={video_id}",
        "--skip-download",
        "--write-auto-sub",        # auto captions
        "--write-sub",             # uploader captions
        "--sub-format", "vtt",
        "-o", base                 # no extension here; yt-dlp adds it
    ]

    # if lang requested, pass it
    if lang:
        command.extend(["--sub-lang", lang])

    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # detect generated file
    generated_file = None
    for file in os.listdir("."):
        if file.startswith(base) and file.endswith(".vtt"):
            generated_file = file
            break

    if not generated_file:
        return None

    # Convert .vtt → text (removing timestamps & formatting)
    text_lines = []
    with open(generated_file, "r", encoding="utf-8") as f:
        for line in f:
            if "-->" in line or line.strip().isdigit() or line.strip() == "" or line.startswith("WEBVTT"):
                continue
            text_lines.append(line.strip())

    # cleanup
    try:
        os.remove(generated_file)
    except Exception:
        pass

    return " ".join(text_lines)
