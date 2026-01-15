# main.py
import streamlit as st
import os
from pathlib import Path
from utils.chunk_utils import chunk_text, preview_chunks, group_chunks
from utils.transcript_utils import extract_video_id, load_youtube_transcript
from utils.whisper_utils import transcribe_audio
from dotenv import load_dotenv
load_dotenv()

# agents
from agents.formatter_agent import format_text
from agents.summarizer_agent import summarize_chunk, summarize_final
from agents.validator_agent import validate_summary_text
from agents.query_agent import answer_from_notes
from agents.translator_agent import translate_text

import concurrent.futures

# Detect if running on Streamlit Community Cloud
IS_STREAMLIT_CLOUD = (
    os.getenv("STREAMLIT_SHARING") == "true"
    or os.getenv("STREAMLIT_SERVER_RUNNING") == "true"
    or os.getenv("STREAMLIT_CLOUD") == "true"
    or "streamlit" in os.getenv("HOSTNAME", "").lower()
)


# Ensuring that required folders exist for saving downloads, transcripts, summaries, audio, etc.
for folder in ["data", "data/downloads", "data/transcripts", "data/summaries", ".data/audio"]:
    os.makedirs(folder, exist_ok=True)

# Streamlit page configuration
st.set_page_config(page_title="YouTube Video Summarization System", page_icon="🤖", layout="wide")
st.title("🧠 Multi-Agentic YouTube Video Summarization System Powered by Whisper and Google ADK")

# Input: YouTube URL
video_url = st.text_input("Enter a YouTube Video URL:", placeholder="https://www.youtube.com/watch?v=xxxx")

# Selection of Translation/Transcription mode
transcription_mode = st.selectbox(
    "Transcription / Translation mode",
    ("Translate to English (Uses Whisper & fast)", "Auto (no Whisper)", "Translate to...")
)   
#Auto - Use available subtitles if present; otherwise, transcribe audio in original language.
#Translate to English (Whisper fast) - Use available English subtitles if present; otherwise, use Whisper to transcribe and translate to English.
#Translate to... - Transcribe audio in original language (using Whisper if needed) and then translate to specified target language using ADK.


target_language = "English"
if transcription_mode == "Translate to...":
    target_language = st.text_input("Output language (e.g., Hindi, French, Spanish):", value="Hindi").strip()


# Summary Generation Trigger
if st.button("Generate Summary", type="primary"):

    if not video_url.strip():
        st.warning("Please enter a valid YouTube URL.")
        st.stop()

    video_id = extract_video_id(video_url)

    with st.spinner("Fetching subtitles or transcribing audio…"):

        # If user selected Whisper English translation, try English subtitles first
        subtitle_lang = "en" if transcription_mode == "Translate to English (Uses Whisper & fast)" else None

        transcript = load_youtube_transcript(video_id, lang=subtitle_lang)

        # No subtitles → Whisper fallback

        # No subtitles → Whisper fallback
        if transcript is None:

            # --- CLOUD SAFETY GUARD ---
            if IS_STREAMLIT_CLOUD:
                st.error(
                    "⚠️ This video does not have subtitles.\n\n"
                    "On the hosted demo, audio transcription is disabled due to "
                    "YouTube restrictions on cloud servers.\n\n"
                    "👉 Please try a video with subtitles, or run the project locally "
                    "to enable Whisper-based audio transcription."
                )
                st.stop()

            # --- LOCAL WHISPER FALLBACK ---
            st.info("📜 Transcript not found → Using Whisper fallback.")

            # A) Auto: transcribe only
            if transcription_mode == "Auto (no Whisper)":
                transcript = transcribe_audio(video_url, translate=False)

            # B) Whisper direct English translate
            elif transcription_mode == "Translate to English (Uses Whisper & fast)":
                transcript = transcribe_audio(video_url, translate=True, target_language="en")

            # C) Multilingual: transcribe → ADK translate
            else:
                transcript = transcribe_audio(video_url, translate=False)
                if target_language.lower() not in ("en", "english"):
                    st.info(f"Translating transcript to {target_language}…")
                    transcript = translate_text(transcript, target_language)

        else:
            # If subtitles exist and user wants another language, translate them
            if transcription_mode == "Translate to...":
                if target_language.lower() not in ("en", "english"):
                    st.info(f"Translating subtitles to {target_language}…")
                    transcript = translate_text(transcript, target_language)

    # Chunking and grouping transcript into batches
    raw_chunks = chunk_text(transcript)
    batches = group_chunks(raw_chunks, batch_size=10)
    preview_chunks(batches)

    #1. FORMAT each batch in parallel
    with st.spinner("Formatting text…"):
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
            formatted_batches = list(ex.map(format_text, batches))

    #2. CHUNK SUMMARIES in parallel
    with st.spinner("Summarizing chunks…"):
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
            chunk_summaries = list(ex.map(summarize_chunk, formatted_batches))

    combined_summary = "\n\n".join(chunk_summaries)

    #3. FINAL SUMMARY
    with st.spinner("Creating final lecture-style summary…"):
        final_summary_text = summarize_final(combined_summary)

    # Optional translation of final summary
    if transcription_mode == "Translate to...":
        if target_language.lower() not in ("en", "english"):
            with st.spinner(f"Translating final summary to {target_language}…"):
                final_summary_text = translate_text(final_summary_text, target_language)

    # Save to session
    st.session_state["final_summary"] = final_summary_text

    #4. VALIDATE SUMMARY
    with st.spinner("Validating summary…"):
        validate_summary_text(final_summary_text)

    st.success("Summary Generated Successfully!")

# Display final summary if available
if "final_summary" in st.session_state:
    st.markdown(st.session_state["final_summary"])
    st.divider()

# Follow-up Question Section
st.subheader("💬 Ask Follow-up Questions")

user_query = st.text_input("Ask something about the summarized notes:")

if st.button("Ask"):
    if "final_summary" not in st.session_state:
        st.error("Please generate a summary first.")
        st.stop()

    with st.spinner("Thinking…"):
        answer = answer_from_notes(st.session_state["final_summary"], user_query)

    st.write(answer)
