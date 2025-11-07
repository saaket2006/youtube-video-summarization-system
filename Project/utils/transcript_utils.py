import subprocess
import os
import uuid

def extract_video_id(url):
    if "v=" in url:
        return url.split("v=")[-1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[-1].split("?")[0]
    return None

def load_youtube_transcript(video_id):
    # Unique filename
    base = f"sub_{uuid.uuid4().hex}"
    subtitle_file = base + ".vtt"

    # yt-dlp command to download auto OR manual English subtitles
    command = [
        "yt-dlp",
        f"https://www.youtube.com/watch?v={video_id}",
        "--skip-download",
        "--write-auto-sub",        # ✅ auto captions
        "--write-sub",             # ✅ uploader captions
        "--sub-lang", "en",
        "--sub-format", "vtt",
        "-o", base                 # ✅ important change (no extension here)
    ]

    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Now detect *actual* generated file
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
    os.remove(generated_file)

    return " ".join(text_lines)
