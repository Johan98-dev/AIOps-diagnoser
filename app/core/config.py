from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "AIOps Diagnoser"
    version: str = "0.1.0"
    groq_api_key: str
    llm_model: str = "llama-3.3-70b-versatile"
    
    # OpenTelemetry & Observability settings
    otel_exporter_otlp_endpoint: Optional[str] = None
    
    # Langfuse LLMOps settings
    langfuse_public_key: Optional[str] = None
    langfuse_secret_key: Optional[str] = None
    langfuse_host: Optional[str] = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
