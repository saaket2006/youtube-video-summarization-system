# main_adk.py
import streamlit as st
import os
from pathlib import Path
from utils.chunk_utils import chunk_text, preview_chunks, group_chunks
from utils.transcript_utils import extract_video_id, load_youtube_transcript
from utils.whisper_utils import transcribe_audio

# agents
from agents.formatter_adk import format_text
from agents.summarizer_adk import summarize_chunk, summarize_final
from agents.validator_adk import validate_summary_text
from agents.query_adk import answer_from_notes

# translator agent (for arbitrary target languages)
from agents.translator_adk import translate_text

import concurrent.futures

# ensure folders
for folder in ["data", "data/downloads", "data/transcripts", "data/summaries"]:
    os.makedirs(folder, exist_ok=True)

st.set_page_config(page_title="YouTube Video Summarization (ADK)", page_icon="🤖", layout="wide")
st.title("🧠 YouTube Video Summarization System Powered by Google ADK")

video_url = st.text_input("Enter a YouTube Video URL:", placeholder="https://www.youtube.com/watch?v=xxxx")

# --- Translation / transcription mode UI ---
transcription_mode = st.selectbox(
    "Transcription mode",
    ("Auto (no translate)", "Translate to English (Whisper fast)", "Translate to...")
)
target_language = "English"
if transcription_mode == "Translate to...":
    target_language = st.text_input("Target language (e.g., Hindi, French, en):", value="English").strip()

if st.button("Generate Summary", type="primary"):

    if not video_url.strip():
        st.warning("Please enter a valid YouTube URL.")
        st.stop()

    with st.spinner("Analyzing video and preparing agents…"):

        video_id = extract_video_id(video_url)

        # Try to download a transcript/subtitles first (don't force 'en' unless user requested)
        subtitle_lang = None
        # If user explicitly chose "Translate to English (Whisper fast)" we still attempt to get subtitles in English first
        if transcription_mode == "Translate to English (Whisper fast)":
            subtitle_lang = "en"

        transcript = load_youtube_transcript(video_id, lang=subtitle_lang)

        if transcript is None:
            st.info("Transcript unavailable → Using Whisper fallback")
            # call whisper transcribe with translate option when appropriate
            if transcription_mode == "Auto (no translate)":
                transcript = transcribe_audio(video_url, translate=False)
            elif transcription_mode == "Translate to English (Whisper fast)":
                transcript = transcribe_audio(video_url, translate=True, target_language="en")
            else:
                # Translate to arbitrary target language: whisper -> then ADK translate (whisper doesn't support non-EN translation directly)
                transcript = transcribe_audio(video_url, translate=False)
                if target_language and target_language.lower() not in ("en", "english"):
                    st.info(f"Translating transcript to {target_language} via ADK...")
                    transcript = translate_text(transcript, target_language)
        else:
            # We have subtitle text. If user requested translation to non-default target, perform it.
            if transcription_mode == "Translate to English (Whisper fast)":
                # subtitles were requested in en; if they exist we already have English transcript
                pass
            elif transcription_mode == "Translate to...":
                if target_language and target_language.lower() not in ("en", "english"):
                    st.info(f"Translating downloaded subtitles to {target_language} via ADK...")
                    transcript = translate_text(transcript, target_language)
                else:
                    # user asked for English target but we downloaded another language; if subtitle_lang wasn't set earlier, attempt translation to English
                    if subtitle_lang is None:
                        # subtitles may be in any language; translate to English if requested
                        pass  # keep as-is

        # Proceed with chunking and summarization as before
        raw_chunks = chunk_text(transcript, max_chars=3000)
        transcript_batches = group_chunks(raw_chunks, batch_size=10)
        preview_chunks(transcript_batches)

        # 1. FORMAT each batch in parallel
        with st.spinner("Formatting transcript batches..."):
            with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
                formatted_batches = list(ex.map(format_text, transcript_batches))

        # 2. CHUNK SUMMARIES in parallel
        with st.spinner("Summarizing chunks..."):
            with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
                chunk_summaries = list(ex.map(summarize_chunk, formatted_batches))

        all_chunk_summaries = "\n\n".join(chunk_summaries)

        # 3. FINAL SUMMARY
        with st.spinner("Creating final lecture-style summary..."):
            final_summary_text = summarize_final(all_chunk_summaries)

        # Save to session
        st.session_state["final_summary"] = final_summary_text

        # 4. VALIDATE
        with st.spinner("Validating summary..."):
            validation_result = validate_summary_text(final_summary_text)

        st.success("Summary Generated Successfully!")

# DISPLAY SUMMARY (IF EXISTS)

if "final_summary" in st.session_state:
    st.markdown(st.session_state["final_summary"])
    st.divider()

# Q&A (NOW OUTSIDE THE GENERATION BLOCK)

st.subheader("💬 Ask Follow-up Questions")

user_query = st.text_input("Enter your question here:")

if st.button("Ask"):
    if "final_summary" not in st.session_state:
        st.error("Please generate a summary first.")
        st.stop()

    with st.spinner("Thinking..."):
        answer = answer_from_notes(
            st.session_state["final_summary"],
            user_query
        )

    st.write(answer)