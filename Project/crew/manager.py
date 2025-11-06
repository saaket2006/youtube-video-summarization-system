from crewai import Agent
from crewai.llm import LLM

llm = LLM(
    provider="groq",
    model="llama-3.1-8b-instant"
)

manager = Agent(
    role="Coordinator",
    goal="Direct the pipeline and ensure summary quality.",
    backstory="You evaluate outputs and request refinements when needed.",
    llm=llm,
    allow_delegation=True,
    verbose=True
)
