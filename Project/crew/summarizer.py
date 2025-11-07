from crewai import Agent, LLM

summarizer = Agent(
    role="Video Summarizer",
    goal="Produce a clear, structured, section-based summary of the transcript.",
    backstory=(
        "You are an expert explainer known for simplifying complex ideas with clarity. "
        "You create structured summaries with meaningful section headers and bullet points."
    ),
    llm=LLM(model="groq/llama-3.1-8b-instant"),
    verbose=True,
    memory=True
)
