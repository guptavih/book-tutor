from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    project_name: str = "AI Book Tutor"
    environment: str = "development"
    logfire_token: str = ""
    database_url: str = "sqlite+aiosqlite:///./tutor.db"
    redis_url: str = "redis://localhost:6379/0"
    chroma_path: str = "./chroma_data"
    groq_api_key: str = ""
    llm_provider: str = "groq"
    llm_model: str = "openai/gpt-oss-120b"

settings = Settings()