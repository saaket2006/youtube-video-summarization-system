from crewai import Agent

query_agent = Agent(
    role="Q&A Assistant",
    goal="Answer user questions based on final summary only.",
    backstory="Helpful and accurate.",
    llm={
        "provider": "groq",
        "model": "llama-3.1-8b-instant"
    },
    verbose=True
)
