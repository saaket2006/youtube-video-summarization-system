# adk_adapter.py
import os
import google.generativeai as genai

class ADKAdapter:
    """
    Adapter that uses Google Gemini API cleanly.
    Falls back to litellm if GEMINI_API_KEY is missing.
    """

    def __init__(self, model: str = "gemini-2.0-flash"):
        self.model_name = model

        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.backend = "gemini"
            self.model = genai.GenerativeModel(model)
        else:
            # fallback: litellm
            import litellm
            self.backend = "litellm"
            self.litellm = litellm
            litellm.api_key = os.getenv("LITELLM_API_KEY")

    def complete(self, prompt: str, temperature: float = 0.2, max_tokens: int = 1024):
        if self.backend == "gemini":
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens
                }
            )
            return response.text

        elif self.backend == "litellm":
            resp = self.litellm.completion(
                model=self.model_name,
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return resp

        else:
            raise RuntimeError("No valid backend found in ADKAdapter.")
