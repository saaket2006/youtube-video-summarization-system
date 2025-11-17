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


def load_youtube_transcript(video_id, lang=None):
    base = f"sub_{uuid.uuid4().hex}"

    cmd = [
        "yt-dlp",
        f"https://www.youtube.com/watch?v={video_id}",
        "--skip-download",
        "--write-auto-sub",
        "--write-sub",
        "--sub-format", "vtt",
        "-o", base
    ]

    if lang:
        cmd += ["--sub-lang", lang]

    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    generated_file = None
    for f in os.listdir("."):
        if f.startswith(base) and f.endswith(".vtt"):
            generated_file = f
            break

    if not generated_file:
        return None

    lines = []
    with open(generated_file, "r", encoding="utf-8") as f:
        for line in f:
            if "-->" in line or line.strip().isdigit() or line.strip() == "" or line.startswith("WEBVTT"):
                continue
            lines.append(line.strip())

    try: os.remove(generated_file)
    except: pass

    return " ".join(lines)
