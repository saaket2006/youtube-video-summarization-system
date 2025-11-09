from crewai import Agent, LLM

# ✅ Faster & Cheaper Summarizer for Chunk Summaries
chunk_summarizer = Agent(
    role="Chunk Summarizer",
    goal="Summarize transcript chunks into short structured notes.",
    backstory=(
        "You provide efficient and concise summaries focused on capturing the key ideas "
        "and main structure of the content. You avoid unnecessary details here."
    ),
    llm=LLM(
        model="groq/llama-3.1-70b-instant"
    ),
    verbose=True,
    memory=False
)

# ✅ High-Quality Summarizer for Final Lecture Notes
final_summarizer = Agent(
    role="Final Summarizer",
    goal="Combine all chunk summaries to create complete, well-structured lecture notes.",
    backstory="A professor-level writer skilled in producing high-quality study material.",
    llm=LLM(
        model="gemini/gemini-2.5-flash"
    ),
    verbose=True,
    memory=False
)
