# 🎥 Multi-Agentic YouTube Video Summarization Tool Powered by Whisper and LLMs

This project is a **YouTube Video Summarization Tool** built using:
- **CrewAI** (Multi-agent reasoning pipeline)
- **Groq LLaMA 3** (Fast + high-quality text reasoning)
- **Gemini LLM Models** (Medium-paced, High tokens per minute)
- **Whisper Speech-to-Text** (Fallback transcription when transcripts aren't available)
- **Streamlit** UI

The tool creates **structured lecture-style study notes**, perfect for:
- Students
- Self-learners
- Researchers
- Exam preparation

---

## ✨ Features

✅ Fetches official YouTube transcript automatically  
✅ If unavailable → Transcribes audio using Whisper  
✅ Splits transcript into chunks  
✅ Summarizes chunks in parallel  
✅ Merges them into **clear college-level lecture notes**  
✅ Allows users to **ask questions** about the video afterward  
✅ Works on **protected / partially restricted** videos using cookies  
✅ Supports **Groq free tier** efficiently with token management  

---

## 📦 How to Run

--> Put in your API Key in the .env file   
--> Check for API   
    export $(grep -v '^#' .env | xargs)   
    echo $GROQ_API_KEY   
--> pip install -r requirements.txt   
--> sudo apt-get update && sudo apt-get install -y ffmpeg    
--> Check for cookies    
    echo "cookies.txt" >> .gitignore   
    git status --ignored --short   
--> streamlit run main.py
