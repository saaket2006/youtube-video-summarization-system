from pytube import YouTube
import whisper

def transcribe_audio(url):
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(only_audio=True).first()
        audio_file = stream.download(filename="audio.mp4")

    except Exception:
        # retry with bypass mode
        yt = YouTube(url, use_oauth=False, allow_oauth_cache=True)
        stream = yt.streams.filter(only_audio=True).first()
        audio_file = stream.download(filename="audio.mp4")

    model = whisper.load_model("base")
    result = model.transcribe(audio_file)
    return result["text"]