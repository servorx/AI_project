from pydantic import BaseSettings

class Settings(BaseSettings):
    ENV: str = "dev"

    GEMINI_API_KEY: str
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""

    COLLECTION_NAME: str = "company_kb"

    class Config:
        env_file = "./.env"

settings = Settings()
