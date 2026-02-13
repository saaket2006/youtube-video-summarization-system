# 🎥 Multi-Agent YouTube Video Summarization System Powered by Whisper and Google ADK

This project is an AI-powered end-to-end system designed to automatically generate structured, clean, and academically styled summaries of YouTube videos. Using a multi-agent pipeline developed with Google’s AI Development Kit (ADK), the system orchestrates transcript extraction, audio transcription, chunking, agent-based task decomposition, translation, and validation to produce high-quality summaries suitable for research and learning. Users simply provide a YouTube URL and an optional translation preference, and the ADK-driven agent workflow handles the complete lifecycle, including post-summary Q&A based on the final output.


## Problem Statement

YouTube offers a vast collection of educational and technical content, but a significant portion of it is long, unstructured, and difficult to process efficiently. Many videos lack accurate transcripts, making it even harder for students, researchers, and multilingual audiences to extract meaningful insights. Manually summarizing videos requires substantial effort, is inconsistent, and is not scalable when working with large volumes of content. These limitations create a clear need for an automated, reliable, and structured summarization mechanism.



## Architecture

The architecture is composed of multiple agents and utility layers that work together in a clean, modular pipeline:

*Transcript Retrieval Layer* -  
transcript_utils: Loads official YouTube transcripts when available.  
whisper_utils: Performs Whisper audio transcription when transcripts are unavailable.

*Chunking Layer* -    
chunk_utils: Splits long transcripts into smaller text segments.   
batch_chunks: Organizes these segments into manageable batches for parallel processing.

*Formatter Agent* - Cleans transcript chunks, fixes grammar, restructures sentences, and improves readability.

*Chunk Summarizer Agent* - Summarizes each cleaned chunk independently. Ensures clarity, structure, and removal of unnecessary content.

*Final Summarizer Agent* - Aggregates all chunk summaries. Produces a polished, section-wise final summary.

*Translator Agent* - Converts the final English summary into the user’s selected language. Preserves headings, bullets, and markdown structure.

*Validator Agent* - Performs correctness, coherence, and structural validation of the final summary. Ensures that the content meets academic-style requirements.

*Q&A Agent* - Allows users to ask follow-up questions. Responds using the final summary as the contextual knowledge base.


## Workflow

The workflow describes how the system processes user input from start to end:

Step 1: User provides YouTube URL and selects translation mode.    
Step 2: System extracts video ID and attempts transcript retrieval.    
Step 3: If transcript is unavailable, Whisper performs audio transcription.    
Step 4: Transcript is chunked into smaller text batches.    
Step 5: *Parallel processing begins*: Formatter Agent cleans each chunk; Chunk Summarizer Agent generates chunk-level summaries.    
Step 6: All chunk summaries are aggregated and merged.    
Step 7: Final Summarizer Agent produces a complete structured summary.    
Step 8: If translation is enabled, Translator Agent converts the summary into the chosen language.    
Step 9: Validator Agent checks the final output for quality and formatting.     
Step 10: Streamlit UI displays the summary and enables the Q&A interaction.    
Step 11: Q&A Agent responds to user queries using the summary as context.    


## Project Structure   

The project is organized into modular components, each handling a specific part of the YouTube summarization workflow. The structure is as follows:    

- main.py
   - Main Streamlit application that connects the user interface with the ADK-based multi-agent pipeline.

- agents/ - Contains all Google ADK agents used throughout the summarization process.    
   - formatter_agent.py – Cleans and restructures raw transcript chunks.
   - summarizer_agent.py –
      - chunk_summarizer – Summarizes cleaned chunks in parallel.
      - final_summarizer – Merges all chunk summaries into a polished final summary.
   - translator_agent.py – Translates the final summary into the selected language.
   - validator_agent.py – Ensures correctness, structure, and academic readability.
   - query_agent.py – ADK-powered agent that answers user questions using the final summary as context.

- utils/ - Contains utility modules required by the agents.
   - transcript_utils.py – Retrieves YouTube transcripts when available.
   - whisper_utils.py – Performs Whisper-based audio transcription if needed.
   - chunk_utils.py – Splits the full transcript into smaller batches.

- .env - Stores sensitive keys and environment configuration (not committed to Git).

- requirements.txt - Dependency list for all required Python packages.

- README.md - Complete documentation for the entire project.

## Agent Design Clarification

While the system is implemented using multiple specialized agents, the execution flow is predefined and deterministic. Agents do not perform autonomous planning, dynamic tool selection, or self-directed goal optimization. Instead, each agent operates within a structured orchestration pipeline designed to ensure reliability, reproducibility, and consistent output quality.   

## Setup and Running Instructions

You can run this project either locally (make sure you have ffmpeg installed) or through GitHub Codespaces (Whisper ASR is faster locally than in Codespaces).    

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
3. Run the main file
```
streamlit run Project/amin.py
```
4. Reconfigure PyTorch (optional) - If PyTorch isn't working, use the following commands (according to your GPU's CUDA version)
```
pip uninstall -y torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130
```

## Conclusion    

The AI-Based YouTube Summarization System demonstrates how a structured multi-agent workflow, powered by Google ADK, can transform long-form video content into clear, concise, and academically reliable summaries. By integrating transcript retrieval, Whisper transcription, chunk-based processing, intelligent summarization, translation, and validation, the system delivers an automated pipeline that is both robust and highly scalable. The architecture ensures that each agent performs a dedicated function, leading to consistent output quality and improved user experience. Ultimately, this project provides a practical and efficient solution for learners, researchers, and professionals who require fast and accurate extraction of meaningful insights from YouTube videos.



## Value Statement   

This project holds significant value by enabling users to consume educational and technical YouTube content more efficiently and effortlessly. By reducing hours of video content into structured summaries within seconds, the system enhances productivity, accessibility, and knowledge retention. The multilingual capability broadens inclusivity, while the ADK-driven agent pipeline ensures reliability and modular extensibility. Whether used for academic research, note-taking, content analysis, or rapid learning, the system delivers tangible benefits by saving time, improving comprehension, and enabling deeper engagement with complex material.


### ⚠️ Note:
For videos without subtitles, Whisper-based audio transcription works reliably in local environments. Due to YouTube restrictions on cloud servers, audio download may fail on hosted demos. Videos with subtitles may work normally. For full functionality, run the project locally.
