from crewai import Agent

loader = Agent(
    role="Transcript Loader",
    goal="Load transcript if available.",
    backstory="Understands how to fetch YouTube transcripts.",
    llm="groq/llama-3.1-8b-instant",
    verbose=True
)
