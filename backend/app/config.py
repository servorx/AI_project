from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Ambiente: dev | prod | staging
    ENV: str = Field(default="dev")

    # Gemini / Google GenAI
    GEMINI_API_KEY: str = Field(..., description="API Key for Google Gemini")
    GEMINI_MODEL: str = Field(default="models/text-bison-001", description="Model for Google Gemini")
    GEMINI_EMBEDDING_MODEL: str = Field(default="models/embedding-gecko-001", description="Embedding model for Google Gemini")

    # Qdrant
    QDRANT_URL: str = Field(default="http://localhost:6333")
    QDRANT_API_KEY: str = Field(default="")
    QDRANT_COLLECTION: str = Field(default="company_kb")
    EMBED_MODEL: str = Field(default="text-bison-001")
    
    # Langroid - LangGraph
    LANGSMITH_API_KEY: str = Field(..., description="API Key for Langroid")
    LANGSMITH_TRACING_V2: bool = Field(default=True, description="Enable tracing for Langroid")
    LANGSMITH_PROJECT: str = Field(default="langroid-ai-project", description="Project name for Langroid")
    TAVILY_API_KEY: str = Field(..., description="API Key for Langroid")

    # MySQL
    MYSQL_USER: str = Field(..., description="User for MySQL")
    MYSQL_PASSWORD: str = Field(..., description="Password for MySQL")
    MYSQL_HOST: str = Field(..., description="Host for MySQL")
    MYSQL_PORT: str = Field(..., description="Port for MySQL")
    MYSQL_DB: str = Field(..., description="Database for MySQL")
    # Sistema general
    # DEBUG: bool = Field(default=True)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
