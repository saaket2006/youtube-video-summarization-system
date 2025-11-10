import streamlit as st
import os
import time
import litellm
from dotenv import load_dotenv
from crewai import Crew, Task, Process

# ---- Import Agents ----
from crew.validator import validator
from crew.loader import loader
from crew.transcriber import transcriber
from crew.formatter import formatter
from crew.summarizer import chunk_summarizer, final_summarizer
from crew.query_agent import query_agent

# ---- Import Utils ----
from utils.chunk_utils import chunk_text
from utils.transcript_utils import extract_video_id, load_youtube_transcript
from utils.whisper_utils import transcribe_audio

for folder in ["data", "data/downloads", "data/transcripts", "data/summaries"]:
    os.makedirs(folder, exist_ok=True)


litellm.RATE_LIMIT_RETRY = True
litellm.RATE_LIMIT_RETRY_MAX_RETRIES = 5
litellm.RATE_LIMIT_RETRY_BACKOFF = 10  # exponential


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

        # Step 1: Validate Transcript Source
        load_task = Task(
            description="Verify transcript is correctly loaded and ready for processing. Return OK if valid.",
            agent=manager,
            expected_output="A confirmation that the transcript is valid and ready."
        )

        # Step 2: Clean Each Transcript Chunk (done in parallel)
        format_tasks = [
            Task(
                description=f"Clean and fix readability of this chunk:\n\n{chunk}",
                agent=formatter,
                asynchronous=True,        # ✅ Run all formatting tasks in parallel
                expected_output="A cleaned, grammatically correct, readable version of the text."
            ) for chunk in transcript_chunks
        ]

        summary_tasks = [
            Task(
                description="Summarize this cleaned chunk into key structured notes.",
                agent=chunk_summarizer,
                asynchronous=True,         # ✅ Run all summarization tasks in parallel
                expected_output="A concise but meaningful bullet-point style summary of the chunk."
            ) for _ in transcript_chunks
        ]


        # Step 4: Merge Summaries into Lecture-Style Notes
        final_summary_task = Task(
            description=(
                "Combine all chunk summaries into clear, structured and long (not too long) college-level lecture notes.\n\n"
                "Guidelines:\n"
                "- Maintain the original flow of ideas in the video.\n"
                "- Break the content into meaningful logical sections.\n"
                "- Use paragraphs to explain concepts clearly.\n"
                "- Use bullet points when listing steps, examples, features, or arguments.\n"
                "- Preserve examples, analogies, and important reasoning.\n"
                "- Highlight important terminology or definitions using **bold**.\n\n"
                "Output Format (to be referrenced, can change according to the topic):\n"
                "# Title\n"
                "## Overview\n"
                "Short paragraph introducing the topic and purpose.\n\n"
                "## Section Title\n"
                "Paragraph explanation.\n"
                "- Supporting bullet point\n"
                "- Supporting bullet point\n\n"
                "## Next Section Title\n"
                "(Repeat structure)\n\n"
                "## Key Takeaways\n"
                "- 5 to 10 core insights\n\n"
                "## One-Line Summary\n"
                "A single sentence that captures the main message."
            ),
            agent=final_summarizer,
            context=summary_tasks,
            expected_output="Structured and detailed lecture-style notes in Markdown."
        )

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

        # Step 6: Prepare Q&A Agent
        qa_task = Task(
            description="Prepare the content so user questions about the video or related to the video can be answered accurately.",
            agent=query_agent,
            expected_output="Ready state confirmation and conceptual grounding for Q&A."
        )

        refine_task = Task(
            description=(
                "Review the final summary for clarity and structure. "
                "If it is generally correct and readable, APPROVE IT. "
                "Do NOT request further refinements unless major errors exist."
                "Check coherence and structure only. Do not rewrite or expand content."
            ),
            agent=manager,
            expected_output="Approved final summary."
        )


        # ---------------- CREW PIPELINE (Hierarchical + Parallel) ----------------
        crew = Crew(
            agents=[loader, transcriber, formatter, chunk_summarizer, final_summarizer, validator, query_agent],
            tasks=format_tasks + summary_tasks + [final_summary_task, validate_task, qa_task],
            process=Process.sequential,
            max_iterations=1,
            verbose=True
        )

        result = crew.kickoff()


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
