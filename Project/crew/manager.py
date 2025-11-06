from crewai import Agent

manager = Agent(
    role="Coordinator",
    goal="Direct workflow, evaluate quality, and request refinements when needed.",
    backstory="Experienced supervisor who ensures structured summarization.",
    llm="groq/llama-3.1-8b-instant",
    allow_delegation=True,
    verbose=True
)
