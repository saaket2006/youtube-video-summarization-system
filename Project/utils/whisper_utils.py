from pytube import YouTube
import whisper

def transcribe_audio(url):
    yt = YouTube(url)
    stream = yt.streams.get_audio_only()
    audio_file = stream.download(filename="audio.mp4")

    model = whisper.load_model("base")
    result = model.transcribe(audio_file)
    return result["text"]