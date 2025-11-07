from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

def extract_video_id(url):
    if "v=" in url:
        return url.split("v=")[-1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[-1].split("?")[0]
    return None

def load_youtube_transcript(video_id):
    try:
        # List available transcripts
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Prefer English transcript if available
        transcript = transcript_list.find_transcript(['en'])
        transcript_data = transcript.fetch()

        return " ".join([entry['text'] for entry in transcript_data])

    except (TranscriptsDisabled, NoTranscriptFound):
        # Return None so Whisper fallback triggers in main.py
        return None
