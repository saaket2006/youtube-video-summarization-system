import streamlit as st
import os
from crewai import Agent, Task, Crew, Process
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptDisabled
from pytube import YouTube
from dotenv import load_dotenv
import whisper

st.set_page_config(page_title="YouTube Summarizer AI", page_icon="🤖", layout="wide")
st.title("🤖 AI-YouTube Video Summarizer")
st.markdown("Several Agents working together to provide you a clean and sectional summary of YouTube videos.")

# Load environment variables
load_dotenv()
groq_key = os.getenv("GROQ_API_KEY", "")
if groq_key:
    os.environ["GROQ_API_KEY"] = groq_key


# Extracting the video ID
def extract_video_id(url):
    if "v=" in url:
        return url.split("v=")[-1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[-1].split("?")[0]
    return None


video_url = st.text_input("Enter a YouTube video URL", placeholder="https://www.youtube.com/watch?v=....")

if st.button("Get Summary", type="primary"):
    if not video_url.strip():
        st.warning("Please enter a YouTube URL!")
    else:
        with st.spinner("The agents are working to provide you a summary..."):
            try:
                video_id = extract_video_id(video_url)
                yt = YouTube(video_url)
                st.write(f"**🎬 Title:** {yt.title}")

                # Whisper fallback
                def transcribe_audio():
                    st.info("🎧 Transcribing audio using Whisper...")
                    stream = yt.streams.filter(only_audio=True).first()
                    audio_file = stream.download(filename="audio.mp4")
                    model = whisper.load_model("base")
                    result = model.transcribe(audio_file)
                    return result["text"]

                # Load official transcript
                def load_transcript():
                    try:
                        st.info("📜 Fetching YouTube Transcript...")
                        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
                        return " ".join([x['text'] for x in transcript_data])
                    except TranscriptDisabled:
                        st.warning("⚠️ Transcript not available — using Whisper fallback.")
                        return transcribe_audio()

                raw_transcript = load_transcript()

                # AGENTS DEFINITION
                manager = Agent(
                    role="Manager",
                    goal="Coordinate all agents and maintain summary quality.",
                    backstory="You oversee the summarization workflow and decide what happens next.",
                    llm="groq/llama-3.1-8b-instant",
                    allow_delegation=True,
                    verbose=True
                )

                loader = Agent(
                    role="Transcript Loader",
                    goal="Load the transcript content.",
                    backstory="Knows how to fetch transcripts quickly.",
                    llm="groq/llama-3.1-8b-instant",
                    verbose=True
                )

                transcriber = Agent(
                    role="Transcriber",
                    goal="Convert audio to text when transcript is unavailable.",
                    backstory="Uses Whisper to create accurate transcripts.",
                    llm="groq/llama-3.1-8b-instant",
                    verbose=True
                )

                formatter = Agent(
                    role="Formatter",
                    goal="Make the transcript grammatically correct and readable.",
                    backstory="Experienced English editor.",
                    llm="groq/llama-3.1-8b-instant",
                    verbose=True
                )

                summarizer = Agent(
                    role="Summarizer",
                    goal="Summarize into clear sections with key points.",
                    backstory="Professional summarizer with structured thinking.",
                    llm="groq/llama-3.1-8b-instant",
                    verbose=True
                )

                query_agent = Agent(
                    role="Q&A Assistant",
                    goal="Answer user questions based on the summary.",
                    backstory="Helps clarify and explore content meaningfully.",
                    llm="groq/llama-3.1-8b-instant",
                    verbose=True
                )
                
                # TASKS
                load_task = Task(
                    description=f"Here is the transcript:\n\n{raw_transcript}\n\nDecide whether the transcript is usable or Whisper should be triggered.",
                    agent=manager
                )

                format_task = Task(
                    description=f"Clean the following transcript for readability:\n\n{raw_transcript}",
                    agent=formatter
                )

                summary_task = Task(
                    description="Summarize the cleaned transcript into structured sections (Intro, Key Insights, Examples, Final Takeaways).",
                    agent=summarizer
                )

                refine_task = Task(
                    description="Review the summary. If unclear, ask summarizer to refine; if good, approve it.",
                    agent=manager
                )

                qa_task = Task(
                    description="Be ready to answer user questions about the summary.",
                    agent=query_agent
                )
                
                # CREW HIERARCHICAL EXECUTION
                crew = Crew(
                    agents=[manager, loader, transcriber, formatter, summarizer, query_agent],
                    tasks=[load_task, format_task, summary_task, refine_task, qa_task],
                    process=Process.HIERARCHICAL,
                    manager_agent=manager,
                    verbose=True
                )

                result = crew.run()

                # OUTPUT DISPLAY
                st.subheader("✅ Sectional Summary:")
                st.write(result)

                st.divider()
                st.subheader("💬 Ask Follow-up Questions About the Video:")
                query = st.text_input("Ask your question here...")

                if st.button("Ask"):
                    response = query_agent.run(query)
                    st.write(response)

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
