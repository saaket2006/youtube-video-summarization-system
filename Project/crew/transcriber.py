from crewai import Agent
from crewai.llm import LLM

llm = LLM(
    provider="groq",
    model="llama-3.1-8b-instant"
)

transcriber = Agent(
    role="Transcriber",
    goal="Convert audio to text when transcripts are unavailable.",
    backstory="Uses Whisper for accurate audio transcription.",
    llm=llm,
    verbose=True
)
