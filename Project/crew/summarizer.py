from crewai import Agent, LLM

# ✅ Faster & Cheaper Summarizer for Chunk Summaries
chunk_summarizer = Agent(
    role="Chunk Summarizer",
    goal="Summarize transcript chunks into short structured notes.",
    backstory=(
        "You provide efficient and concise summaries focused on capturing the key ideas "
        "and main structure of the content. You avoid unnecessary details here."
    ),
    llm=LLM(model="groq/llama-3.1-3b-preview"),  # ✅ smaller model to avoid rate limits
    verbose=True,
    memory=False
)

# ✅ High-Quality Summarizer for Final Lecture Notes
final_summarizer = Agent(
    role="Lecture Note Generator",
    goal="Generate detailed, well-structured, college-level lecture notes.",
    backstory=(
        "You create clear, organized explanations designed for students. "
        "You maintain logical flow, preserve examples, and produce refined notes."
    ),
    llm=LLM(model="groq/llama-3.1-8b-instant"),  # ✅ high quality model for final synthesis
    verbose=True,
    memory=True
)
