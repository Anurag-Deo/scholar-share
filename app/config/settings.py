import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    # LLM Configuration
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")

    # Model Configuration
    HEAVY_MODEL_PROVIDER: str = os.getenv("HEAVY_MODEL_PROVIDER", "openai")
    HEAVY_MODEL_NAME: str = os.getenv("HEAVY_MODEL_NAME", "gpt-4-turbo")
    HEAVY_MODEL_API_KEY: str = os.getenv("HEAVY_MODEL_API_KEY", "")
    HEAVY_MODEL_BASE_URL: str | None = os.getenv("HEAVY_MODEL_BASE_URL")

    LIGHT_MODEL_PROVIDER: str = os.getenv("LIGHT_MODEL_PROVIDER", "openai")
    LIGHT_MODEL_NAME: str = os.getenv("LIGHT_MODEL_NAME", "gpt-3.5-turbo")
    LIGHT_MODEL_API_KEY: str = os.getenv("LIGHT_MODEL_API_KEY", "")
    LIGHT_MODEL_BASE_URL: str | None = os.getenv("LIGHT_MODEL_BASE_URL")

    # API Keys
    DEVTO_API_KEY: str = os.getenv("DEVTO_API_KEY", "")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./scholarshare.db")

    # Application Settings
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "7860"))


settings = Settings()
