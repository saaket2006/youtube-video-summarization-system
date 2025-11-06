import streamlit as st
import os
from crewai import Agent, Task, Crew, Process
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptDisabled
from pytube import YouTube
from dotenv import load_dotenv
import whisper

# -------------------- CONFIG --------------------
st.set_page_config(page_title="YouTube Summarizer AI", page_icon="🤖", layout="wide")
st.title("🤖 AI-YouTube Video Summarizer")
st.markdown("Multiple agents collaborate to provide a refined, sectional summary of YouTube videos.")

load_dotenv()
groq_key = os.getenv("GROQ_API_KEY", "")
if groq_key:
    os.environ["GROQ_API_KEY"] = groq_key


# -------------------- HELPERS --------------------
def extract_video_id(url):
    if "v=" in url:
        return url.split("v=")[-1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[-1].split("?")[0]
    return None


def chunk_text(text, max_chars=3500):
    """Split transcript so each chunk fits model context."""
    chunks = []
    while len(text) > max_chars:
        split_index = text.rfind('.', 0, max_chars)
        if split_index == -1:
            split_index = max_chars
        chunks.append(text[:split_index].strip())
        text = text[split_index:].strip()
    chunks.append(text)
    return chunks


# -------------------- UI --------------------
video_url = st.text_input("Enter a YouTube video URL", placeholder="https://www.youtube.com/watch?v=xxxx")


if st.button("Get Summary", type="primary"):
    if not video_url.strip():
        st.warning("Please enter a YouTube URL!")
        st.stop()

    with st.spinner("Processing… Please wait…"):
        try:
            video_id = extract_video_id(video_url)
            yt = YouTube(video_url)
            st.write(f"🎬 **Title:** {yt.title}")

            # ---- Transcript or Whisper Fallback ----
            def transcribe_audio():
                st.info("🎧 No transcript available. Using Whisper transcription…")
                stream = yt.streams.filter(only_audio=True).first()
                audio_file = stream.download(filename="audio.mp4")
                model = whisper.load_model("base")
                result = model.transcribe(audio_file)
                return result["text"]

            def load_transcript():
                try:
                    st.info("📜 Fetching YouTube transcript…")
                    transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
                    return " ".join([x['text'] for x in transcript_data])
                except TranscriptDisabled:
                    return transcribe_audio()

            raw_transcript = load_transcript()
            transcript_chunks = chunk_text(raw_transcript)

            # -------------------- AGENTS --------------------
            manager = Agent(
                role="Manager",
                goal="Coordinate, evaluate and refine output quality.",
                backstory="You supervise all agents and ensure excellent summaries.",
                llm="groq/llama-3.1-8b-instant",
                allow_delegation=True,
                verbose=True
            )

            loader = Agent(
                role="Transcript Loader",
                goal="Ensure transcript is available and usable.",
                backstory="Knows where to fetch transcripts.",
                llm="groq/llama-3.1-8b-instant",
                verbose=True
            )

            formatter = Agent(
                role="Formatter",
                goal="Fix grammar, formatting, readability.",
                backstory="Skilled English language editor.",
                llm="groq/llama-3.1-8b-instant",
                verbose=True
            )

            summarizer = Agent(
                role="Summarizer",
                goal="Summarize content into structured sections.",
                backstory="Professional summarizer.",
                llm="groq/llama-3.1-8b-instant",
                verbose=True
            )

            query_agent = Agent(
                role="Q&A Assistant",
                goal="Answer follow-up questions accurately.",
                backstory="Helps users understand the summary deeper.",
                llm="groq/llama-3.1-8b-instant",
                verbose=True
            )

            # -------------------- TASKS --------------------
            load_task = Task(
                description=f"Evaluate and confirm transcript readiness:\n\n{raw_transcript[:2000]}...",
                agent=manager
            )

            # Format chunks (Runs IN PARALLEL)
            format_tasks = [
                Task(
                    description=f"Clean this transcript chunk:\n\n{chunk}",
                    agent=formatter,
                    asynchronous=True
                ) for chunk in transcript_chunks
            ]

            # Summarize chunks (Runs IN PARALLEL)
            summary_tasks = [
                Task(
                    description="Summarize the cleaned chunk into structured key points.",
                    agent=summarizer,
                    asynchronous=True
                ) for _ in transcript_chunks
            ]

            # Merge final summary
            final_summary_task = Task(
                description="Merge all chunk summaries into one cohesive, sectional summary.",
                agent=summarizer
            )

            # Final refinement
            refine_task = Task(
                description="Review the final summary for clarity and quality. Refine only if necessary.",
                agent=manager
            )

            qa_task = Task(
                description="Be available to answer follow-up questions.",
                agent=query_agent
            )

            # -------------------- CREW EXECUTION --------------------
            crew = Crew(
                agents=[manager, loader, formatter, summarizer, query_agent],
                tasks=[load_task] + format_tasks + summary_tasks + [final_summary_task, refine_task, qa_task],
                process=Process.HIERARCHICAL,
                manager_agent=manager,
                max_iterations=2,
                verbose=True
            )

            result = crew.run()

            # -------------------- DISPLAY SUMMARY --------------------
            st.subheader("✅ **Sectional Summary:**")
            st.write(result)

            st.divider()

            # -------------------- Q&A --------------------
            st.subheader("💬 Ask follow-up questions about the video:")
            query = st.text_input("Ask here...")

            if st.button("Ask"):
                answer = query_agent.run(query)
                st.write(answer)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
