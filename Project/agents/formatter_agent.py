# agents/formatter_adk.py
from agents.agent_base import ADKAgent

formatter = ADKAgent(
    role="Transcript Formatter",
    goal="Clean and rewrite transcript text to be readable and grammatically correct.",
    backstory="A linguistic expert specializing in simplifying and polishing language.",
    model="gemini-2.0-flash",
    temperature=0.25
)

def format_text(text: str):
    prompt = f"Please clean and rewrite the following transcript to be readable and grammatically correct. Preserve meaning.\n\nTEXT:\n{text}"
    return formatter.run(prompt, max_tokens=2048)
