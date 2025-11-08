from crewai import Agent, LLM
from utils.retry_utils import safe_llm_call
from litellm import SafeDict

llm = LLM(model="groq/llama-3.1-8b-instant")

loader = Agent(
    role="Transcript Loader",
    goal="Load transcript if available.",
    backstory="Understands how to fetch YouTube transcripts.",
    llm=LLM(
        model="groq/llama-3.1-8b-instant",
        call=SafeDict(call=safe_llm_call)  # ✅ This overrides the call method
    ),
    verbose=True
)
