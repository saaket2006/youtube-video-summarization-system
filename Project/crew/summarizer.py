from crewai import Agent, LLM
from utils.retry_utils import safe_llm_call
from litellm import SafeDict

# ✅ Faster & Cheaper Summarizer for Chunk Summaries
chunk_summarizer = Agent(
    role="Chunk Summarizer",
    goal="Summarize transcript chunks into short structured notes.",
    backstory=(
        "You provide efficient and concise summaries focused on capturing the key ideas "
        "and main structure of the content. You avoid unnecessary details here."
    ),
    llm=LLM(
        model="groq/llama-3.1-70b-instant",
        call=safe_llm_call
    ),
    verbose=False,
    memory=False
)

# ✅ High-Quality Summarizer for Final Lecture Notes
final_summarizer = Agent(
    role="Final Summarizer",
    goal="Combine all chunk summaries to create complete, well-structured lecture notes.",
    backstory="A professor-level writer skilled in producing high-quality study material.",
    llm=LLM(
        model="openai/gpt-4o",
        call=safe_llm_call
    ),  # ✅ Best for long structured notes
    verbose=True,
    memory=False
)
