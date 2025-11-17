# agents/translator_adk.py
from adk_adapter import ADKAdapter

translator_adapter = ADKAdapter()

def translate_text(text: str, target_language: str = "English") -> str:
    prompt = (
        f"Translate the following text into {target_language}. "
        "Preserve meaning and formatting. Keep paragraphs and bullet points intact if present.\n\n"
        f"TEXT:\n{text}"
    )
    return translator_adapter.complete(prompt, temperature=0.0, max_tokens=4096)
