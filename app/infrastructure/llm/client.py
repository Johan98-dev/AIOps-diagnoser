import json
import os
from typing import Dict, Any
from app.core.config import settings

class LlmClient:
    """Concrete adapter for interfacing with Groq API via standard OpenAI client with optional Langfuse tracing."""

    def __init__(self):
        self.model = settings.llm_model

        # Configure Langfuse environment if keys are provided
        if settings.langfuse_public_key and settings.langfuse_secret_key:
            os.environ["LANGFUSE_PUBLIC_KEY"] = settings.langfuse_public_key
            os.environ["LANGFUSE_SECRET_KEY"] = settings.langfuse_secret_key
            if settings.langfuse_host:
                os.environ["LANGFUSE_HOST"] = settings.langfuse_host
            try:
                from langfuse.openai import AsyncOpenAI as LangfuseAsyncOpenAI
                self.client = LangfuseAsyncOpenAI(
                    api_key=settings.groq_api_key,
                    base_url="https://api.groq.com/openai/v1"
                )
                return
            except ImportError:
                pass

        # Fallback to standard AsyncOpenAI client
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(
            api_key=settings.groq_api_key,
            base_url="https://api.groq.com/openai/v1"
        )

    async def generate_diagnosis(self, prompt: str, system_instruction: str) -> Dict[str, Any]:
        """
        Sends the generated prompt and system instructions to Groq.
        Forces JSON response format to match Pydantic schema structure.
        Renders telemetry traces to Langfuse if configured.
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
