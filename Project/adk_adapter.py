# adk_adapter.py
import os
import google.generativeai as genai

class ADKAdapter:
    """
    Clean adapter using ONLY Google Gemini API.
    No litellm. No Vertex AI. No ADC required.
    """

    def __init__(self, model: str = "gemini-2.0-flash"):
        self.model_name = model

        # Fetch API key from environment variables (.env file)
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is missing. Add it to your .env file.")

        # configure Gemini API
        genai.configure(api_key=api_key)

        # initialize model
        self.model = genai.GenerativeModel(model)

    def complete(self, prompt: str, temperature: float = 0.2, max_tokens: int = 1024):
        """Generate text using Gemini."""
        response = self.model.generate_content(
            prompt,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens
            }
        )

        return response.text
