import httpx
import logging

logger = logging.getLogger(__name__)

class OllamaClient:
    """
    Async client for interacting with Ollama API
    """
    def __init__(self, base_url: str = "http://localhost:8000/health", model_name: str = "mistral"):
        self.base_url = base_url
        self.model_name = model_name

    async def generate_text(self, prompt: str, http_client: httpx.AsyncClient):
        """
        Send a prompt to the Ollama model and return generated text
        """
        try:
            logger.info(f"Sending prompt to Ollama model: {self.model_name}")
            response = await http_client.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model_name, "prompt": prompt},
                timeout=60.0,
            )

            if response.status_code != 200:
                logger.error(f"Ollama error {response.status_code}: {response.text}")
                return f"Error: Ollama model failed ({response.status_code})"

            # Ollama streams responses; combine the text parts
            output = ""
            async for line in response.aiter_lines():
                if line.strip():
                    output += line
            return output.strip()
        
        except Exception as e:
            logger.error(f"Ollama request failed: {str(e)}")
            return "Error: Could not generate response from Ollama"