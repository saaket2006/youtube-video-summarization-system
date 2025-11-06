from crewai import Agent
from crewai.llm import LLM

llm = LLM(
    provider="groq",
    model="llama-3.1-8b-instant"
)

formatter = Agent(
    role="Formatter",
    goal="Improve clarity, flow, and grammar while preserving meaning.",
    backstory="Expert in English text refinement.",
    llm=llm,
    verbose=True
)
