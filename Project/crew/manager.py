from crewai import Agent, LLM

manager = Agent(
    role="Manager",
    goal="Coordinate agents and maintain workflow quality.",
    backstory="Oversees the summarization pipeline and ensures output quality.",
    llm=LLM(
        model="groq/meta-llama/llama-4-scout-17b-16e-instruct"
    ),
    verbose=False,
    memory=False
)
