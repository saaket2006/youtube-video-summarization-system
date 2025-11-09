from crewai import Agent, LLM

llm = LLM(model="groq/llama-3.1-8b-instant")

loader = Agent(
    role="Transcript Loader",
    goal="Load transcript if available.",
    backstory="Understands how to fetch YouTube transcripts.",
    llm=LLM(
        model="groq/llama-3.1-8b-instant"
    ),
    verbose=True
)
