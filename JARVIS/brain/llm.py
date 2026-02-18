"""LLM client for connecting to Ollama API."""

import json
from typing import Generator

import requests

from ..core.config import MODEL_CONFIG, OLLAMA_BASE_URL
from ..core.logger import get_logger

logger = get_logger(__name__)


class OllamaClient:
    """Client for interacting with Ollama LLM API."""
    
    def __init__(self, base_url: str = OLLAMA_BASE_URL, model: str | None = None) -> None:
        """Initialize Ollama client.
        
        Args:
            base_url: Ollama API base URL
            model: Model name (defaults to MODEL_CONFIG.llm_model)
        """
        self.base_url = base_url.rstrip("/")
        self.model = model or MODEL_CONFIG.llm_model
        
        logger.info(f"OllamaClient initialized (model: {self.model}, url: {self.base_url})")
    
    def is_available(self) -> bool:
        """Check if Ollama server is running.
        
        Returns:
            True if server is accessible, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to Ollama at {self.base_url}")
            return False
        except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
            logger.error(f"Error checking Ollama availability: {e}")
            return False
    
    def chat(
        self, 
        messages: list[dict[str, str]], 
        stream: bool = False
    ) -> str | Generator[str, None, None]:
        """Send chat messages to Ollama.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            stream: If True, yields tokens as they arrive. If False, returns complete response.
            
        Returns:
            Complete response string if stream=False
            Generator yielding tokens if stream=True
            
        Raises:
            RuntimeError: If Ollama is not available or request fails
        """
        if not self.is_available():
            raise RuntimeError(f"Ollama server not available at {self.base_url}")
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream
        }
        
        logger.debug(f"Sending chat request to Ollama (stream={stream})")
        logger.debug(f"Messages: {json.dumps(messages, indent=2)}")
        
        try:
            if stream:
                return self._chat_stream(payload)
            else:
                return self._chat_complete(payload)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama request failed: {e}")
            raise RuntimeError(f"Ollama request failed: {e}") from e
    
    def _chat_complete(self, payload: dict) -> str:
        """Send request and return complete response.
        
        Args:
            payload: Request payload
            
        Returns:
            Complete response text
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            
            data = response.json()
            content = data.get("message", {}).get("content", "")
            
            logger.debug(f"Ollama response: {content[:100]}...")
            return content
            
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out")
            raise RuntimeError("Ollama request timed out after 120 seconds")
        except requests.exceptions.HTTPError as e:
            logger.error(f"Ollama HTTP error: {e}")
            raise RuntimeError(f"Ollama HTTP error: {e}") from e
    
    def _chat_stream(self, payload: dict) -> Generator[str, None, None]:
        """Send request and stream tokens.
        
        Args:
            payload: Request payload
            
        Yields:
            Response tokens as they arrive
        """
        try:
            with requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                stream=True,
                timeout=120
            ) as response:
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if "message" in data and "content" in data["message"]:
                                token = data["message"]["content"]
                                yield token
                            
                            # Check if done
                            if data.get("done", False):
                                break
                                
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse streaming response line: {line}")
                            continue
                            
        except requests.exceptions.Timeout:
            logger.error("Ollama streaming request timed out")
            raise RuntimeError("Ollama streaming request timed out")
        except requests.exceptions.HTTPError as e:
            logger.error(f"Ollama HTTP error: {e}")
            raise RuntimeError(f"Ollama HTTP error: {e}") from e
    
    def list_models(self) -> list[str]:
        """List available models on Ollama server.
        
        Returns:
            List of model names
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            
            data = response.json()
            models = [model["name"] for model in data.get("models", [])]
            
            logger.info(f"Available Ollama models: {models}")
            return models
            
        except (requests.exceptions.RequestException, json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to list models: {e}")
            return []
