# crew/validator.py
from crewai import Agent, LLM

validator = Agent(
    role="Summary Validator",
    goal="Check lecture notes for structure, completeness, and clarity. Approve or suggest minimal fixes.",
    backstory=(
        "You are a precise academic proofreader. You do NOT rewrite everything; "
        "you verify that notes are usable for study and provide short improvement suggestions if needed."
    ),
    llm=LLM(
        model="groq/llama-3.1-8b-instant",  # lightweight, high-speed model
        max_tokens=256,
        temperature=0.2
    ),
    memory=False,
    verbose=True
)