from crewai import Agent

transcriber = Agent(
    role="Transcriber",
    goal="Convert audio to text when transcripts are unavailable.",
    backstory="Uses Whisper for accurate audio transcription.",
    llm="groq/llama-3.1-8b-instant",
    verbose=True
)
