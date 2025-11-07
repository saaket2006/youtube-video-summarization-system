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
    # Temporary filename
    subtitle_file = f"sub_{uuid.uuid4().hex}.vtt"

    command = [
        "yt-dlp",
        f"https://www.youtube.com/watch?v={video_id}",
        "--skip-download",
        "--write-auto-sub",        # IMPORTANT: auto-generated captions (solves your issue)
        "--sub-lang", "en",
        "--sub-format", "vtt",
        "-o", subtitle_file
    ]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError:
        return None

    # Read the VTT file
    vtt_file = subtitle_file + ".en.vtt"
    if not os.path.exists(vtt_file):
        return None

    # Convert VTT → text
    transcript_text = []
    with open(vtt_file, "r", encoding="utf-8") as f:
        for line in f:
            # Skip timecodes and metadata
            if "-->" in line or line.strip().isdigit() or line.startswith("WEBVTT"):
                continue
            clean = line.strip()
            if clean:
                transcript_text.append(clean)

    os.remove(vtt_file)
    return " ".join(transcript_text)
