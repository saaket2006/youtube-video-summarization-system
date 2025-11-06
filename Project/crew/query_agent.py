from crewai import Agent
from crewai.llm import LLM

llm = LLM(
    provider="groq",
    model="llama-3.1-8b-instant"
)

query_agent = Agent(
    role="Q&A Assistant",
    goal="Answer user questions based on final summary only.",
    backstory="Helpful and accurate.",
    llm=llm,
    verbose=True
)
