import streamlit as st
import os
from dotenv import load_dotenv
from crewai import Crew, Task, Process

# ---- Import Agents ----
from crew.manager import manager
from crew.loader import loader
from crew.transcriber import transcriber
from crew.formatter import formatter
from crew.summarizer import summarizer
from crew.query_agent import query_agent

# ---- Import Utils ----
from utils.chunk_utils import chunk_text
from utils.transcript_utils import extract_video_id, load_youtube_transcript
from utils.whisper_utils import transcribe_audio

for folder in ["data", "data/downloads", "data/transcripts", "data/summaries"]:
    os.makedirs(folder, exist_ok=True)
    
# ---------------- STREAMLIT UI SETUP ----------------
st.set_page_config(page_title="YouTube Summarizer AI", page_icon="🎬", layout="wide")
st.title("🤖 AI YouTube Video Summarizer")
st.markdown("Multiple agents collaborate to provide a refined, structured summary.")

load_dotenv()
groq_key = os.getenv("GROQ_API_KEY", "")
if groq_key:
    os.environ["LITELLM_API_KEY"] = os.getenv("GROQ_API_KEY")


video_url = st.text_input("Enter a YouTube Video URL:", placeholder="https://www.youtube.com/watch?v=xxxx")


# ---------------- MAIN EXECUTION TRIGGER ----------------
if st.button("Generate Summary", type="primary"):

    if not video_url.strip():
        st.warning("Please enter a valid YouTube URL.")
        st.stop()

    with st.spinner("Analyzing video and preparing agents…"):

        video_id = extract_video_id(video_url)

        # --- Load Transcript or Use Whisper Fallback ---
        transcript = load_youtube_transcript(video_id)

        if transcript is None:
            st.info("📜 Transcript unavailable → Using Whisper to transcribe audio…")
            transcript = transcribe_audio(video_url)

        # Chunk transcript for parallel summarization
        transcript_chunks = chunk_text(transcript)

        # ---------------- TASK DEFINITIONS ----------------
        load_task = Task(
            description=f"Confirm transcript content quality:\n\n{transcript[:2000]}...",
            agent=manager
        )

        # Clean each chunk
        format_tasks = [
            Task(
                description=f"Clean and fix readability of this chunk:\n\n{chunk}",
                agent=formatter,
                asynchronous=True
            ) for chunk in transcript_chunks
        ]

        # Summarize each chunk
        summary_tasks = [
            Task(
                description="Summarize this cleaned chunk into key structured points.",
                agent=summarizer,
                asynchronous=True
            ) for _ in transcript_chunks
        ]

        # Merge summaries into one structured final summary
        final_summary_task = Task(
            description=(
                "You are given a cleaned transcript of a YouTube video. "
                "Rewrite the content into detailed, structured lecture-style study notes. "
                "The notes must:\n"
                "1) Follow the video's topic flow.\n"
                "2) Be divided into clear, meaningful sections.\n"
                "3) Explain concepts thoroughly in full sentences.\n"
                "4) Preserve examples, analogies, and reasoning steps.\n"
                "5) Highlight important terms.\n\n"
                "Format to follow:\n\n"
                "# Title\n"
                "## 1. Video Overview (short paragraph)\n"
                "## 2. Section Name\n"
                "Detailed explanation paragraphs.\n"
                "- Bullet points for supporting ideas\n"
                "> Important term or quoted insight\n\n"
                "## Final Key Takeaways (5–10 bullets)\n"
                "## One-Sentence Core Message\n"
            ),
            agent=summarizer,
            context=[chunk_summaries],
            expected_output="Lecture style notes in structured markdown."
        )


        # Manager refinement
        refine_task = Task(
            description="Review final summary quality and refine if necessary.",
            agent=manager
        )

        # Q&A agent ready state
        qa_task = Task(
            description="Prepare to answer user questions.",
            agent=query_agent
        )

        # ---------------- CREW PIPELINE (Hierarchical + Parallel) ----------------
        crew = Crew(
            agents=[manager, loader, transcriber, formatter, summarizer, query_agent],
            tasks=[load_task] + format_tasks + summary_tasks + [final_summary_task, refine_task, qa_task],
            process=Process.HIERARCHICAL,
            manager_agent=manager,
            max_iterations=2,
            verbose=True
        )

        result = crew.run()

        # ---------------- DISPLAY SUMMARY ----------------
        st.subheader("✅ Final Sectional Summary")
        st.write(result)

        st.divider()

        # ---------------- Q&A INTERACTION ----------------
        st.subheader("💬 Ask Follow-up Questions About the Video")
        user_query = st.text_input("Enter your question here:")

        if st.button("Ask"):
            answer = query_agent.run(user_query)
            st.write(answer)
