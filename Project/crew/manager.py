from crewai import Agent, LLM
from utils.retry_utils import safe_llm_call
from litellm import SafeDict

manager = Agent(
    role="Manager",
    goal="Coordinate agents and maintain workflow quality.",
    backstory="Oversees the summarization pipeline and ensures output quality.",
    llm=LLM(
        model="groq/llama-3.1-8b-instant",
        call=SafeDict(call=safe_llm_call)  # ✅ This overrides the call method
    ),
    verbose=False,
    memory=False
)
