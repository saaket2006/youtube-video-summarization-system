# crew/validator.py
from crewai import Agent, LLM

# ✅ Lightweight Validator Agent
validator = Agent(
    role="Summary Validator",
    goal="Check if the lecture notes are clear, complete, and structured. Improve them if needed.",
    backstory=(
        "You are a careful academic reviewer. You fix weak parts like missing sections, unclear flow, "
        "or formatting. If everything looks fine, just approve it."
    ),
    llm=LLM(
        model="groq/llama-3.1-8b-instant",
        temperature=0.25
    ),
    verbose=True
)


# ✅ Functional helper to validate and optionally improve the summary
def validate_summary(summary_text: str) -> str:
    """
    Check if the summary is complete and well-structured.
    If it looks weak or too short, the validator agent will improve it once.
    """
    # simple rule checks
    if len(summary_text.split()) < 100:
        feedback = "The summary is too short. Expand it with more details and examples."
    elif "#" not in summary_text and "-" not in summary_text:
        feedback = "The summary lacks structure. Add headings or bullet points for clarity."
    else:
        feedback = "APPROVED"

    # if all good, return unchanged
    if feedback == "APPROVED":
        return summary_text

    print(f"🧩 Validator Feedback: {feedback}")
    prompt = f"Improve this summary based on feedback:\n{feedback}\n\n{summary_text}"

    improved_summary = validator.run(prompt)
    return improved_summary
