from crewai import Agent

formatter = Agent(
    role="Formatter",
    goal="Improve clarity, flow, and grammar while preserving meaning.",
    backstory="Expert in English text refinement.",
    llm={
        "provider": "groq",
        "model": "llama-3.1-8b-instant"
    },
    verbose=True
)
