# agents/validator_adk.py
from agents.adk_base import ADKAgent

validator = ADKAgent(
    role="Summary Validator",
    goal="Check if lecture notes are clear, complete and structured.",
    backstory="Careful academic reviewer.",
    model="gemini-2.5-flash",
    temperature=0.25
)

def validate_summary_text(summary_text: str):
    prompt = (
        "You are a validator. If the notes are complete, coherent and well-structured, reply exactly: APPROVED. "
        "Otherwise, give 2-3 short bullet points with improvement suggestions.\n\n"
        + summary_text
    )
    return validator.run(prompt, max_tokens=2048)
