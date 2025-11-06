from crewai import Agent

summarizer = Agent(
    role="Summarizer",
    goal="Convert cleaned text into structured, meaningful summaries.",
    backstory="Skilled at extracting key insights.",
    llm={
        "provider": "groq",
        "model": "llama-3.1-8b-instant"
    },
    verbose=True
)
