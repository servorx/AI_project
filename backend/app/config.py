from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Ambiente: dev | prod | staging
    ENV: str = Field(default="dev")

    # Gemini / Google GenAI
    GEMINI_API_KEY: str = Field(default="", description="API Key for Google Gemini")
    GEMINI_MODEL: str = Field(default="gemini-2.5-flash", description="Model for Google Gemini")
    GEMINI_EMBEDDING_MODEL: str = Field(default="text-embedding-004", description="Embedding model for Google Gemini")

    # Qdrant
    QDRANT_URL: str = Field(default="http://localhost:6333")
    QDRANT_API_KEY: str = Field(default="")
    QDRANT_COLLECTION: str = Field(default="company_kb")

    # Langroid / LangGraph (opcional hasta integrarlo)
    USE_LANGGRAPH: bool = Field(default=False)
    # LANGSMITH_API_KEY: str = Field(default="")
    # LANGSMITH_TRACING_V2: bool = Field(default=True)
    # LANGSMITH_PROJECT: str = Field(default="langroid-ai-project")
    # TAVILY_API_KEY: str = Field(default="")

    # WhatsApp (opcional en dev)
    WHATSAPP_PHONE_ID: str = Field(default="")
    WHATSAPP_ACCESS_TOKEN: str = Field(default="")
    WHATSAPP_VERIFY_TOKEN: str = Field(default="test_token")

    # para saber si se ingesta el kb o no (solo desarrollo local)
    SHOW_SOURCES: bool = Field(default=True)
    # MySQL (puedes dejar valores por defecto para dev)
    MYSQL_USER: str = Field(default="root")
    MYSQL_PASSWORD: str = Field(default="password")
    MYSQL_HOST: str = Field(default="127.0.0.1")
    MYSQL_PORT: int = Field(default=3306)
    MYSQL_DB: str = Field(default="omnicanal_db")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
