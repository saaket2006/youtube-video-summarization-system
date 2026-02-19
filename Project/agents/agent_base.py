import time
import logging
from adk_adapter import ADKAdapter

logger = logging.getLogger(__name__)

class ADKAgent:
    """
    Base class for all agents powered by the LLM.
    Each agent has:
    - a role (who it is)
    - a goal (what it should achieve)
    - an optional backstory (helps guide model behaviour)
    This class wraps ADKAdapter for simple prompt-based interactions.
    """
    
    def __init__(self, role: str, goal: str, backstory: str = "", model: str = None, temperature: float = 0.25):
        model = model or "qwen2.5:7b"
        self.client = ADKAdapter(model=model)
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.temperature = temperature

    def run(self, prompt: str, max_tokens: int = 1024) -> str:
        start_time = time.time()
        logger.info(f"🟢 Agent STARTED: {self.role}")
        
        # Build a compact system context + user prompt (you can expand to structured messages if ADK supports it)
        system_content = f"Role: {self.role}\nGoal: {self.goal}\nBackstory: {self.backstory}\n\n"
        # Combine system context with user prompt
        full_prompt = system_content + prompt
        
        result = self.client.complete(full_prompt, temperature=self.temperature, max_tokens=max_tokens)
        
        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"🔴 Agent COMPLETED: {self.role} (Time taken: {duration:.2f}s)")
        
        return result
