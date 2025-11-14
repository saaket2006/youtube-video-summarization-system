import streamlit as st
import os
import time
import litellm
from dotenv import load_dotenv
from crewai import Crew, Task, Process

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

        format_tasks = [
            Task(
                description=f"Clean and fix readability of this transcript segment:\n\n{batch}",
                agent=formatter,
                asynchronous=True,  # run all format tasks concurrently
                expected_output="A cleaned, grammatically correct, readable version of the text."
            )   
            for batch in transcript_batches
        ]

        # ✅ Step 5: Summarize Each Cleaned Batch (also parallelized)
        summary_tasks = [
            Task(
                description=(
                    "Summarize this cleaned transcript batch into key structured notes. "
                    "Focus on clarity, topic flow, and extracting main ideas.\n\n"
                    "Return bullet-style notes or short paragraphs for each concept."
                ),
                agent=chunk_summarizer,
                asynchronous=True,  # parallel summarization for speed
                expected_output="A concise but meaningful bullet-point summary of the batch."
            )
            for _ in transcript_batches
        ]

        # ✅ Step 6: Combine all summaries into final long-form notes
        final_summary_task = Task(
            description=(
                "Combine all batch-level summaries into well-structured, lecture-style notes.\n\n"
                "Guidelines:\n"
                "- Maintain original flow and logical order from the video.\n"
                "- Use headings and subheadings (##) to separate sections.\n"
                "- Write in a clear, instructional tone.\n"
                "- Use bullet points for lists, examples, and features.\n"
                "- Highlight key terms in **bold**.\n\n"
                "Output Format (example):\n"
                "# Title\n"
                "## Overview\n"
                "Short introduction paragraph.\n\n"
                "## Section Title\n"
                "- Supporting point\n"
                "- Example or explanation\n\n"
                "## Key Takeaways\n"
                "- 5–10 concise bullet points summarizing core ideas\n\n"
                "## One-Line Summary\n"
                "A single sentence capturing the entire video message."
            ),
            agent=final_summarizer,
            context=summary_tasks,
            expected_output="Structured, polished lecture-style notes in Markdown format."
        )

        # ✅ Step 7: Prepare Q&A readiness
        qa_task = Task(
            description=(
                "Analyze the final summarized content and prepare it so that "
                "follow-up questions about the lecture can be answered accurately."
            ),
            agent=query_agent,
            expected_output="Confirmation that Q&A context is ready."
        )


       # ---------------- CREW PIPELINE ----------------
        crew = Crew(
            agents=[loader, transcriber, formatter, chunk_summarizer, final_summarizer, validator, query_agent],
            tasks=format_tasks + summary_tasks + [final_summary_task, qa_task],
            process=Process.sequential,
            max_iterations=1,
            verbose=True
        )

        # Run the full pipeline
        result = crew.kickoff()

        # Extract text output from result (Crew can return dict or str)
        final_summary_text = str(result)

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
        #st.subheader("✅ Final Sectional Summary")
        #st.write(final_summary_text)

        st.divider()

        # ---------------- Q&A INTERACTION ----------------
        st.subheader("💬 Ask Follow-up Questions About the Video")
        user_query = st.text_input("Enter your question here:")

        if st.button("Ask"):
            answer = query_agent.run(
                f"Use the following notes to answer the question.\n\nNOTES:\n{final_summary_text}\n\nQUESTION:\n{user_query}"
            )
            st.write(answer)

