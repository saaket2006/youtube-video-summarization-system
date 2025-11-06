from crewai import Agent
from crewai.llm import LLM

llm = LLM(model="groq/llama-3.1-8b-instant")

summarizer = Agent(
    role="Summarizer",
    goal="Convert cleaned text into structured, meaningful summaries.",
    backstory="Skilled at extracting key insights.",
    llm=llm,
    verbose=True
)
