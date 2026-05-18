# 🎥 Multi-Agent YouTube Video Summarization System Powered by Whisper and Ollama (Local LLM)

This project is an AI-powered end-to-end system designed to automatically generate structured, clean, and academically styled summaries of YouTube videos. Using a multi-agent pipeline, the system orchestrates transcript extraction, audio transcription, chunking, agent-based task decomposition, translation, and validation to produce high-quality summaries. Users simply provide a YouTube URL and an optional translation preference, and the agent workflow handles the complete lifecycle, entirely locally using Ollama.

## Problem Statement

YouTube offers a vast collection of educational and technical content, but a significant portion of it is long, unstructured, and difficult to process efficiently. Many videos lack accurate transcripts, making it even harder for students, researchers, and multilingual audiences to extract meaningful insights. Manually summarizing videos requires substantial effort, is inconsistent, and is not scalable when working with large volumes of content. These limitations create a clear need for an automated, reliable, and structured summarization mechanism.

## Architecture

The architecture is composed of multiple agents and utility layers that work together in a clean, modular pipeline:

*Transcript Retrieval Layer* -  
transcript_utils: Loads official YouTube transcripts when available.  
whisper_utils: Performs Whisper audio transcription when transcripts are unavailable.

*Chunking Layer* -    
chunk_utils: Splits long transcripts into large, context-rich batches (optimized for speed).

*Chunk Summarizer Agent* - Summarizes each chunk into high-density technical notes. Focuses on capturing every detail concisely.

*Final Summarizer Agent* - Aggregates all chunk summaries. Produces a comprehensive, lecture-style study guide.

*Translator Agent* - Converts the final English summary into the user’s selected language.

*Validator Agent* - Performs correctness and structural validation of the final summary.

*Q&A Agent* - Allows users to ask follow-up questions with session history.

## Key Features
- **Local LLM Powered**: Uses Ollama (`qwen2.5:3b`) for zero-cost, private inference.
- **High-Density Summaries**: Optimized prompts ensuring comprehensive coverage of every technical point.
- **Speed Optimized**: Smart chunking (12k chars) and removed redundant steps for fast generation (approx 80-90s for 20min video).
- **Q&A with History**: Chat-like interface to ask follow-up questions, with history persisted for the session.
- **Movable UI**: User-friendly input forms that flow with the page content.
- **Robust Logging**: Clear start/stop timing logs for performance monitoring.

## Workflow

The workflow describes how the system processes user input from start to end:

Step 1: User provides YouTube URL and selects translation mode.    
Step 2: System extracts video ID and attempts transcript retrieval.    
Step 3: If transcript is unavailable, Whisper performs audio transcription.    
Step 4: Transcript is chunked into large batches.    
Step 5: *Parallel processing begins*: Chunk Summarizer Agent generates detailed notes for each batch.    
Step 6: All chunk summaries are aggregated.    
Step 7: Final Summarizer Agent produces a complete study guide.    
Step 8: If translation is enabled, Translator Agent converts the summary.    
Step 9: Validator Agent checks the final output.     
Step 10: Streamlit UI displays the summary.    
Step 11: User can ask follow-up questions via the localized Q&A form.


## Project Structure   

The project is organized into modular components, each handling a specific part of the YouTube summarization workflow. The structure is as follows:    

- main.py
   - Main Streamlit application that connects the user interface with the multi-agent pipeline.

- agents/ - Contains all agents used throughout the summarization process.    
   - formatter_agent.py – Cleans and restructures raw transcript chunks.
   - summarizer_agent.py –
      - chunk_summarizer – Summarizes cleaned chunks in parallel.
      - final_summarizer – Merges all chunk summaries into a polished final summary.
   - translator_agent.py – Translates the final summary into the selected language.
   - validator_agent.py – Ensures correctness, structure, and academic readability.
   - query_agent.py – Agent that answers user questions using the final summary as context.

- utils/ - Contains utility modules required by the agents.
   - transcript_utils.py – Retrieves YouTube transcripts when available.
   - whisper_utils.py – Performs Whisper-based audio transcription if needed.
   - chunk_utils.py – Splits the full transcript into smaller batches.

- .env - (Optional) Stores environment configuration.

- requirements.txt - Dependency list for all required Python packages.

- README.md - Complete documentation for the entire project.

## Agent Design Clarification

While the system is implemented using multiple specialized agents, the execution flow is predefined and deterministic. Agents do not perform autonomous planning, dynamic tool selection, or self-directed goal optimization. Instead, each agent operates within a structured orchestration pipeline designed to ensure reliability, reproducibility, and consistent output quality.   

## Setup and Running Instructions

You can run this project locally (make sure you have ffmpeg and Ollama installed).

1. Clone the repository
```
git clone https://github.com/saaket2006/youtube-video-summarization-system.git
```
2. Create a virtual environment and switch to it
```
python -m venv venv
venv\Scripts\activate
```
3. Install the dependencies
```
pip install -r Project/requirements.txt
```
4. Install and Configure Ollama
   - Download and install [Ollama](https://ollama.com/).
   - Pull the default model:
     ```
     ollama pull qwen2.5:3b
     ```
   - Ensure Ollama is running in the background.

5. Run the main file
```
streamlit run Project/amin.py
```
6. Reconfigure PyTorch (optional) - If PyTorch isn't working, use the following commands (according to your GPU's CUDA version)
```
pip uninstall -y torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130
```

## Conclusion    

The AI-Based YouTube Summarization System demonstrates how a structured multi-agent workflow, powered by Google ADK, can transform long-form video content into clear, concise, and academically reliable summaries. By integrating transcript retrieval, Whisper transcription, chunk-based processing, intelligent summarization, translation, and validation, the system delivers an automated pipeline that is both robust and highly scalable. The architecture ensures that each agent performs a dedicated function, leading to consistent output quality and improved user experience. Ultimately, this project provides a practical and efficient solution for learners, researchers, and professionals who require fast and accurate extraction of meaningful insights from YouTube videos.



## Value Statement   

This project holds significant value by enabling users to consume educational and technical YouTube content more efficiently and effortlessly. By reducing hours of video content into structured summaries within seconds, the system enhances productivity, accessibility, and knowledge retention. The multilingual capability broadens inclusivity, while the ADK-driven agent pipeline ensures reliability and modular extensibility. Whether used for academic research, note-taking, content analysis, or rapid learning, the system delivers tangible benefits by saving time, improving comprehension, and enabling deeper engagement with complex material.


### ⚠️ Note:
For videos without subtitles, Whisper-based audio transcription works reliably in local environments. Due to YouTube restrictions on cloud servers, audio download may fail on hosted demos, and LLM also runs locally.
