from crewai import Agent, LLM

formatter = Agent(
    role="Transcript Formatter",
    goal="Clean and rewrite transcript text to be readable and grammatically correct.",
    backstory="A linguistic expert specializing in simplifying and polishing language.",
    llm=LLM(
        model="groq/llama-3.1-8b-instant",
        temperature=0.25
    ),
    verbose=True
)
