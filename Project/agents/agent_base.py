# agents/agent_base.py
from typing import Optional
from adk_adapter import ADKAdapter

class ADKAgent:
    def __init__(self, role: str, goal: str, backstory: str = "", model: str = None, temperature: float = 0.25):
        model = model or "gemini-2.0-flash"
        self.client = ADKAdapter(model=model)
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.temperature = temperature

    def run(self, prompt: str, max_tokens: int = 1024) -> str:
        # Build a compact system context + user prompt (you can expand to structured messages if ADK supports it)
        system_content = f"Role: {self.role}\nGoal: {self.goal}\nBackstory: {self.backstory}\n\n"
        full_prompt = system_content + prompt
        return self.client.complete(full_prompt, temperature=self.temperature, max_tokens=max_tokens)
