from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "AIOps Diagnoser"
    version: str = "0.1.0"
    groq_api_key: str
    llm_model: str = "llama-3.3-70b-versatile"

    class Config:
        env_file = ".env"


settings = Settings()
