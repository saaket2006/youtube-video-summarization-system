from crewai import Agent, LLM

query_agent = Agent(
    role="Q&A Tutor",
    goal="Answer follow-up questions based on final notes.",
    backstory="You are a friendly study assistant who explains clearly.",
    llm=LLM(
        model="groq/llama-3.3-70b-versatile",
        temperature=0.3
    ),
    verbose=True
)
