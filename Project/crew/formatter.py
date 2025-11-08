from crewai import Agent, LLM
from utils.retry_utils import safe_llm_call

formatter = Agent(
    role="Formatter",
    goal="Clean and rewrite transcript text to be readable and grammatically correct.",
    backstory="A linguistic expert specializing in simplifying and polishing language.",
    llm=LLM(
        model="gemini/gemini-1.5-flash",
        call=safe_llm_call
    ),
    verbose=False,
    memory=False
)
