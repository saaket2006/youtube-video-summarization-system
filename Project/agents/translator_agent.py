# agents/translator_adk.py
from adk_adapter import ADKAdapter

adapter = ADKAdapter()

def translate_text(text: str, target_language: str = "English") -> str:
    # Translate text into the specified target language.
    prompt = (
        f"Translate the following text into {target_language}. "
        f"Preserve headings, bullet points and formatting.\n\n{text}"
    )
    return adapter.complete(prompt, temperature=0.0, max_tokens=4096)
