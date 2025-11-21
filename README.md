# 🎥 Multi-Agentic YouTube Video Summarization Tool Powered by Whisper and LLMs

This project is an AI-powered end-to-end system designed to automatically generate structured, clean, and academically styled summaries of YouTube videos. Using a multi-agent pipeline developed with Google’s AI Development Kit (ADK), the system orchestrates transcript extraction, audio transcription, chunking, agent collaboration, translation, and validation to produce high-quality summaries suitable for research and learning. Users simply provide a YouTube URL and an optional translation preference, and the ADK-driven agent workflow handles the complete lifecycle, including post-summary Q&A based on the final output.


## Problem Statement

YouTube offers a vast collection of educational and technical content, but a significant portion of it is long, unstructured, and difficult to process efficiently. Many videos lack accurate transcripts, making it even harder for students, researchers, and multilingual audiences to extract meaningful insights. Manually summarizing videos requires substantial effort, is inconsistent, and is not scalable when working with large volumes of content. These limitations create a clear need for an automated, reliable, and structured summarization mechanism.


## Solution Statement

The AI-Based YouTube Summarization System addresses this challenge by leveraging Google ADK to build an intelligent multi-agent workflow that transforms YouTube videos into high-quality summaries. The system retrieves or transcribes the video, cleans and chunks the text, and uses ADK-powered formatter and summarizer agents running in parallel to process the content efficiently. The outputs are merged by a final summarizer agent, and optional translation is provided through an additional ADK agent. A validator agent ensures correctness, structure, and readability, while a Q&A agent allows users to interact with the summarized material. This tightly orchestrated ADK workflow removes the burden of manual summarization and provides multilingual, academically structured results within seconds.


## Architecture

The architecture is composed of multiple agents and utility layers that work together in a clean, modular pipeline:
<div align="center">
   <img width="4158" height="3685" alt="Architecture" src="https://github.com/user-attachments/assets/a9ee655b-b29f-4090-b735-d7fe2df2c8f7" />
</div>

   
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
<div align="center">
   <img width="539" height="1352" alt="Methodology" src="https://github.com/user-attachments/assets/74758f42-62d6-4d28-b191-2e13b63f7608" />
</div>

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


## Setup and Running Instructions

You can run this project either locally or through GitHub Codespaces.    

*Running Locally* :-    
Clone the repository to your system or download the zip file into your system.    
Create and activate a Python virtual environment.    
Install dependencies with "pip install -r requirements.txt".    
Add your required API keys and environment variables to the appropriate config file or ".env".    
Launch the application using "streamlit run main_adk.py".    
Open the displayed local URL to access the interface.    

*Running on GitHub Codespaces* :-    
Open the repository inside GitHub Codespaces.    
Allow the environment to initialize the dev container.    
Install dependencies by running "pip install -r requirements.txt".    
Ensure that API keys are added to the Codespaces environment variables.    
Start the application using "streamlit run main_adk.py".    
Access the forwarded public URL automatically generated by Codespaces to use the application.
