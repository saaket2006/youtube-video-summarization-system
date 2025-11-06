from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled

def extract_video_id(url):
    if "v=" in url:
        return url.split("v=")[-1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[-1].split("?")[0]
    return None

def load_youtube_transcript(video_id):
    try:
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([x['text'] for x in transcript_data])
    except TranscriptsDisabled:
        return None
