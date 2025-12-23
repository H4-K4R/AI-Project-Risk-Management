import os
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI
 
# Load environment variables from .env file
load_dotenv()
 
 
class LLMClient:
    """
    HuggingFace Inference API client using OpenAI SDK.
    - Uses env var HF_API_TOKEN.
    - Defaults to a free instruct model if none provided.
    - Returns None on failure so callers can gracefully fall back.
    """
 
    def __init__(self, model: Optional[str] = None, timeout: int = 60):
        self.api_token = os.getenv("HF_API_TOKEN")
        # Use provided model, or HF_MODEL env var, or default to a free model
        self.model = model or os.getenv("HF_MODEL") or "meta-llama/Meta-Llama-3-8B-Instruct"
        self.timeout = timeout
       
        # Create OpenAI client pointing to HuggingFace
        if self.api_token:
            self.client = OpenAI(
                base_url="https://router.huggingface.co/v1",
                api_key=self.api_token,
                timeout=self.timeout
            )
        else:
            self.client = None
 
    def available(self) -> bool:
        return bool(self.api_token)
 
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> Optional[str]:
        if not self.available():
            return None
 
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return completion.choices[0].message.content
        except Exception:
            return None
 
 
