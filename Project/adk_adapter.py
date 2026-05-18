import ollama
import logging

# Configure logging if not already configured
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ADKAdapter:
    """
    Clean adapter using ONLY Ollama (local LLM).
    No external API keys required.
    """

    def __init__(self, model: str = "qwen2.5:3b"):
        self.model_name = model
        # No API key needed for Ollama

    def complete(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1024):
        """Generate text using Ollama."""
        # logger.info(f"Generating with model: {self.model_name}")
        logger.debug(f"Prompt: {prompt[:500]}..." if len(prompt) > 500 else f"Prompt: {prompt}")

        try:
            response = ollama.chat(model=self.model_name, messages=[
                {
                    'role': 'user',
                    'content': prompt,
                },
            ], options={
                'temperature': temperature,
                'num_predict': max_tokens
            })
            
            content = response['message']['content']
            logger.debug(f"Response: {content[:500]}..." if len(content) > 500 else f"Response: {content}")
            return content
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise e
