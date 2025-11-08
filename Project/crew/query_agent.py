from crewai import Agent, LLM
from utils.retry_utils import safe_llm_call

query_agent = Agent(
    role="Q&A Tutor",
    goal="Answer follow-up questions based on final notes.",
    backstory="You are a friendly study assistant who explains clearly.",
    llm=LLM(
        model="openai/gpt-4.1-mini",
        call=safe_llm_call   # ✅
    ),
    verbose=True
)
