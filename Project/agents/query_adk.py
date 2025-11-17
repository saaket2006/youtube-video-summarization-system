# agents/query_adk.py
from agents.adk_base import ADKAgent

query_agent = ADKAgent(
    role="Q&A Tutor",
    goal="Answer follow-up questions based on final notes.",
    backstory="Friendly study assistant who explains clearly.",
    model="gemini-2.5-flash",
    temperature=0.3
)

def answer_from_notes(notes_markdown: str, question: str):
    prompt = (
        f"Here are lecture notes:\n\n{notes_markdown}\n\n"
        f"QUESTION:\n{question}\n\n"
        "Answer concisely and reference the relevant headings."
    )
    return query_agent.run(prompt, max_tokens=1024)
