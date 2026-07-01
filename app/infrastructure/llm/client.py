import json
from typing import Dict, Any
from openai import AsyncOpenAI
from app.core.config import settings

class LlmClient:
    """Concrete adapter for interfacing with Groq API via standard OpenAI client."""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.groq_api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        self.model = settings.llm_model

    async def generate_diagnosis(self, prompt: str, system_instruction: str) -> Dict[str, Any]:
        """
        Sends the generated prompt and system instructions to Groq.
        Forces JSON response format to match Pydantic schema structure.
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,  # Lower temperature for more deterministic/factual diagnostic outputs
            )
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Received empty content from Groq LLM API")
            
            return json.loads(content)
        except Exception as e:
            # Handle potential API errors, parsing issues, or rate limits
            raise RuntimeError(f"Failed to generate diagnosis via Groq: {str(e)}") from e
