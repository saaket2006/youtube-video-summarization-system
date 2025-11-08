import streamlit as st
import os
import time
import litellm
from dotenv import load_dotenv
from crewai import Crew, Task, Process

# ---- Import Agents ----
from crew.manager import manager
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
                description="Clean this transcript chunk for grammar, readability, and remove filler words.",
                agent=formatter,
                asynchronous=True,
                expected_output="A cleaned, grammatically improved text chunk."
            ) for chunk in transcript_chunks
        ]

        # Step 3: Summarize Each Cleaned Chunk (done in parallel)
        summary_tasks = [
            Task(
                description="Summarize this chunk into key structured notes with bullet points.",
                agent=chunk_summarizer,
                asynchronous=True,
                expected_output="A concise bullet-point style summary of this chunk."
            ) for _ in transcript_chunks
        ]

        # Step 4: Merge Summaries into Lecture-Style Notes
        final_summary_task = Task(
            description=(
                "Combine all chunk summaries into clear, structured college-level lecture notes.\n\n"
                "Guidelines:\n"
                "- Maintain the original flow of ideas in the video.\n"
                "- Break the content into meaningful logical sections.\n"
                "- Use paragraphs to explain concepts clearly.\n"
                "- Use bullet points when listing steps, examples, features, or arguments.\n"
                "- Preserve examples, analogies, and important reasoning.\n"
                "- Highlight important terminology or definitions using **bold**.\n\n"
                "Output Format:\n"
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

        # Step 6: Prepare Q&A Agent
        qa_task = Task(
            description="Prepare the content so user questions about the video can be answered accurately.",
            agent=query_agent,
            expected_output="A ready-to-answer knowledge representation of the summarized content."
        )

        # ---------------- CREW PIPELINE (Hierarchical + Parallel) ----------------
        crew = Crew(
            agents=[loader, transcriber, formatter, chunk_summarizer, final_summarizer, query_agent],
            tasks=[load_task] + format_tasks + summary_tasks + [final_summary_task, qa_task],
            process=Process.hierarchical,
            manager_agent=manager,
            max_iterations=2,
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
