import time
import random
from litellm import completion, RateLimitError

def safe_llm_call(**params):
    """
    Automatically retries LLM calls when rate-limits occur.
    """
    max_retries = 6
    base_wait = 4  # seconds

    for attempt in range(max_retries):
        try:
            return completion(**params)  # standard call
        except RateLimitError as e:
            wait = base_wait * (2 ** attempt) + random.uniform(0, 1)
            print(f"⚠️ Rate limit hit. Retrying in {wait:.1f}s (attempt {attempt + 1}/{max_retries})…")
            time.sleep(wait)

    raise RuntimeError("❌ Failed after repeated rate-limit retries.")
