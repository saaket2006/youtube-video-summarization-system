from crewai import Agent, LLM

query_agent = Agent(
    role="Q&A Tutor",
    goal="Answer follow-up questions based on final notes.",
    backstory="You are a friendly study assistant who explains clearly.",
    llm=LLM(
        model="gemini/gemini-2.0-flash-lite"
    ),
    verbose=True
)
