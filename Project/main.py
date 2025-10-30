import streamlit as st
import os
from crewai import Agent, Task, Crew, Process
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptDisabled
from pytube import YouTube
from dotenv import load_dotenv
import whisper

st.set_page_config(page_title = "YouTube Summarizer AI", page_icon = "🤖", layout = "wide")
st.title("🤖 AI-YouTube Video Summarizer")
st.markdown("Several Agents working together to provide you a clean and sectional summary of YouTube videos.")

load_dotenv()
groq_key = os.getenv("GROQ_API_KEY", "")
if groq_key:
    os.environ["GROQ_API_KEY"] = groq_key

video_url = st.text_input(
  "Enter a YouTube video URL",
  placeholder="https://www.youtube.com/watch?v=....",
)

# Extracting the video ID
def extract_video_id(url):
  if "v=" in url:
    return url.split("v=")[-1].split("&")[0]
  elif "youtu.be/" in url:
    return url.split("youtu.be/")[-1].split("?")[0]
  return None

#Main execution
if st.button("Get Summary", type="primary"):
  if not video_url.strip():
    st.warning("Please enter a youtube URL!")
  else:
    with st.spinner("The agents are working to provide you a summary"):
      try:
        video_id = extract_video_id(video_url)
        yt = YouTube(video_url)
        st.write(f"**🎬 Title:** {yt.title}")

        def transcribe_audio():
          st.info("🎧 Transcribing audio using Whisper...")
          stream = yt.streams.filter(only_audio=True).first()
          audio_file = stream.download(filename="audio.mp4")
          model = whisper.load_model("base")
          result = model.transcribe(audio_file)
          return result["text"]

        def load_transcript():
          try:
            st.info("Fetching YouTube Transcript......")
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
            return " ".join([x['text'] for x in transcript_data])
          except TranscriptDisabled:
            st.warning("⚠️ Transcript not available — using Whisper fallback.")
            return transcribe_audio()

        manager = Agent(
          role = "Manager",
          goal = "Oversee and co-ordinate youtube summarization process.",
          backstory = "You're a skilled AI project manager. You decide whether to use the official transcript or Whisper transcription, ensure the transcript is clean, and coordinate summarization process.",
          llm = "groq/llama-3.1-8b-instant",
          tools = [],
          verbose = True
        )
        transcriber = Agent(
          role = "Transcriber",
          goal = "Covert the YouTube audio into text using Whisper.",
          backstory = "An AI transcriber who uses Whisper to generate accurate text from audio.",
          llm = "groq/llama-3.1-8b-instant",
          tools = [],
          verbose = True
        )
        loader = Agent(
          role = "Transcript Loader",
          goal = "Load the official YouTube transcript if available.",
          backstory = "An assistant that fetches the YouTube transcript directly from the API.",
          llm = "groq/llama-3.1-8b-instant",
          tools = [],
          verbose = True
        )
        formatter = Agent(
          role = "Formatter",
          goal = "Correct grammar, punctuation, and readability of the transcript.",
          backstory = "You're a skilled English teacher who has a great understanding of grammar. Improve the grammar of the transcript generated.",
          llm = "groq/llama-3.1-8b-instant",
          tools = [],
          verbose = True
        )







