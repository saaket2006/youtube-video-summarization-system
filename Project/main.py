import streamlit as st
import os
import time
import litellm
from dotenv import load_dotenv
from crewai import Crew, Task, Process
from pathlib import Path
# ---- Import Agents ----
from crew.validator import validator, validate_summary
from crew.loader import loader
from crew.transcriber import transcriber
from crew.formatter import formatter
from crew.summarizer import chunk_summarizer, final_summarizer
from crew.query_agent import query_agent

# ---- Import Utils ----
from utils.chunk_utils import chunk_text, preview_chunks, group_chunks
from utils.transcript_utils import extract_video_id, load_youtube_transcript
from utils.whisper_utils import transcribe_audio

for folder in ["data", "data/downloads", "data/transcripts", "data/summaries"]:
    os.makedirs(folder, exist_ok=True)


litellm.RATE_LIMIT_RETRY = True
litellm.RATE_LIMIT_RETRY_MAX_RETRIES = 5
litellm.RATE_LIMIT_RETRY_BACKOFF = 10  # exponential


# ---------------- STREAMLIT UI SETUP ----------------
st.set_page_config(page_title="YouTube Summarizer AI", page_icon="🎬", layout="wide")
st.title("🤖 Multi-Agentic YouTube Video Summarization System Powered by Whisper and LLM")
st.markdown("Multiple agents collaborate to provide a refined, structured summary.")

load_dotenv()
groq_key = os.getenv("GROQ_API_KEY", "")
if groq_key:
    os.environ["LITELLM_API_KEY"] = os.getenv("GROQ_API_KEY")
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

#print("Loaded ENV from:", env_path)
#print("GEMINI_API_KEY =", os.getenv("GEMINI_API_KEY"))

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
        raw_chunks = chunk_text(transcript, max_chars=3000)
        #st.info(f"🧩 Transcript split into {len(raw_chunks)} primary chunks.")

        transcript_batches = group_chunks(raw_chunks, batch_size=10)
        #st.info(f"📦 Grouped into {len(transcript_batches)} batches for summarization.")

        preview_chunks(transcript_batches)

        # ---------------- TASK DEFINITIONS ----------------

        # 1. FORMATTER TASKS
        format_tasks = [
            Task(
                name=f"format_task_{i}",
                description=f"Clean and fix readability of this transcript segment:\n\n{batch}",
                agent=formatter,
                asynchronous=True,
                expected_output="A cleaned, grammatically correct, readable version of the text."
            )
            for i, batch in enumerate(transcript_batches)
        ]

        # 2. CHUNK SUMMARY TASKS
        summary_tasks = [
            Task(
                name=f"summary_task_{i}",
                description=(
                    "Summarize this cleaned transcript batch into key structured notes. "
                    "Focus on clarity, topic flow, and extracting main ideas.\n\n"
                    "Return bullet points ONLY. No long paragraphs."
                ),
                agent=chunk_summarizer,
                asynchronous=True,
                expected_output="Bullet-point structured notes for the batch."
            )
            for i in range(len(transcript_batches))
        ]

        # 3. FINAL SUMMARY TASK (NAMED!)
        final_summary_task = Task(
            name="final_summary",
            description=(
                "Combine all batch-level summaries into well-structured, lecture-style notes.\n\n"
                "STRICT FORMAT RULES:\n"
                "- MUST use headings (#, ##, ###)\n"
                "- MUST use bullet points for content\n"
                "- MUST avoid long paragraphs\n"
                "- MUST include key takeaways\n"
                "- MUST include one-line summary\n"
                "- MUST output clean Markdown\n"
            ),
            agent=final_summarizer,
            context=summary_tasks,
            expected_output="Sectional markdown summary."
        )

        # 4. QA PREPARATION TASK (NAMED!)
        qa_task = Task(
            name="qa_preparation",
            description=(
                "Prepare the final summary content for answering follow-up questions. "
                "Do NOT rewrite the summary. Simply acknowledge readiness."
            ),
            agent=query_agent,
            expected_output="Ready for Q&A."
        )

        # ---------------- CREW PIPELINE ----------------
        crew = Crew(
            agents=[loader, transcriber, formatter, chunk_summarizer, final_summarizer, validator, query_agent],
            tasks=format_tasks + summary_tasks + [final_summary_task, qa_task],
            process=Process.sequential,
            max_iterations=1,
            verbose=True
        )

        # ---------------- RUN PIPELINE ----------------
        result = crew.kickoff()

        # ---------------- EXTRACT REAL FINAL SUMMARY ----------------
        # Extract FINAL SUMMARY (second-last task, because last = QA)
        # Extract FINAL SUMMARY (second-last task output)
        final_summary_task_output = result.tasks_output[-2]
        final_summary_text = final_summary_task_output.raw



        # ✅ Define Validator Task AFTER summary is available
        validate_task = Task(
            description=(
                "Read the final lecture-style notes below. "
                "If they are complete, coherent, and well-structured, reply exactly: APPROVED. "
                "Otherwise, give 2-3 short bullet points with improvement suggestions.\n\n"
                f"{final_summary_text[:4000]}"
            ),
            agent=validator,
            expected_output="APPROVED or short improvement suggestions."
        )

        # Execute validator task properly using a temporary Crew
        validation_crew = Crew(
            agents=[validator],
            tasks=[validate_task],
            process=Process.sequential,
            verbose=True
        )

        validation_result = validation_crew.kickoff()

        # ---------------- DISPLAY FINAL SUMMARY ----------------
        st.subheader("✅ Final Sectional Summary")
        st.markdown(final_summary_text)

        st.divider()

        # ---------------- Q&A INTERACTION ----------------
        st.subheader("💬 Ask Follow-up Questions About the Video")
        user_query = st.text_input("Enter your question here:")

        if st.button("Ask"):
            answer = query_agent.run(
                f"Use the following notes to answer the question.\n\nNOTES:\n{final_summary_text}\n\nQUESTION:\n{user_query}"
            )
            st.write(answer)

