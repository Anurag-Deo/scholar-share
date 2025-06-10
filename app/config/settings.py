import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # dotenv not available, use environment variables directly
    pass


class Settings:
    def __init__(self):
        # Load default values from environment
        self._load_defaults()
        # Runtime overrides - these will be updated from UI
        self._runtime_overrides = {}

    def _load_defaults(self):
        # LLM Configuration
        self.MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")

        # Model Configuration
        self.HEAVY_MODEL_PROVIDER: str = os.getenv("HEAVY_MODEL_PROVIDER", "openai")
        self.HEAVY_MODEL_NAME: str = os.getenv("HEAVY_MODEL_NAME", "gpt-4-turbo")
        self.HEAVY_MODEL_API_KEY: str = os.getenv("HEAVY_MODEL_API_KEY", "")
        self.HEAVY_MODEL_BASE_URL: str | None = os.getenv("HEAVY_MODEL_BASE_URL")

        self.LIGHT_MODEL_PROVIDER: str = os.getenv("LIGHT_MODEL_PROVIDER", "openai")
        self.LIGHT_MODEL_NAME: str = os.getenv("LIGHT_MODEL_NAME", "gpt-3.5-turbo")
        self.LIGHT_MODEL_API_KEY: str = os.getenv("LIGHT_MODEL_API_KEY", "")
        self.LIGHT_MODEL_BASE_URL: str | None = os.getenv("LIGHT_MODEL_BASE_URL")

        self.CODING_MODEL_PROVIDER: str = os.getenv("CODING_MODEL_PROVIDER", "openai")
        self.CODING_MODEL_NAME: str = os.getenv(
            "CODING_MODEL_NAME", "gpt-4-1106-preview"
        )
        self.CODING_MODEL_API_KEY: str = os.getenv("CODING_MODEL_API_KEY", "")
        self.CODING_MODEL_BASE_URL: str | None = os.getenv(
            "CODING_MODEL_BASE_URL",
            "https://api.openai.com/v1/chat/completions",
        )

        # Image Generation
        self.IMAGE_GEN_API_KEY: str = os.getenv("IMAGE_GEN_API_KEY", "")
        self.IMAGE_GEN_BASE_URL: str | None = os.getenv(
            "IMAGE_GEN_BASE_URL",
            "https://api.openai.com/v1/images/generations",
        )
        self.IMAGE_GEN_MODEL: str = os.getenv("IMAGE_GEN_MODEL", "dall-e-3")
        self.IMAGE_GEN_IMAGE_SIZE: str = os.getenv("IMAGE_GEN_IMAGE_SIZE", "1024x1024")
        self.IMAGE_GEN_IMAGE_QUALITY: str = os.getenv(
            "IMAGE_GEN_IMAGE_QUALITY", "standard"
        )
        self.IMAGE_GEN_IMAGE_STYLE: str = os.getenv("IMAGE_GEN_IMAGE_STYLE", "vivid")

        # DeepInfra API for blog images
        self.DEEPINFRA_API_KEY: str = os.getenv("DEEPINFRA_API_KEY", "")

        # API Keys
        self.DEVTO_API_KEY: str = os.getenv("DEVTO_API_KEY", "")

    def get_value(self, key: str):
        """Get value with runtime override support"""
        return self._runtime_overrides.get(key, getattr(self, key, ""))

    def set_override(self, key: str, value: str):
        """Set runtime override for a setting"""
        if value and value.strip():
            self._runtime_overrides[key] = value.strip()
        elif key in self._runtime_overrides:
            # Remove override if empty value provided
            del self._runtime_overrides[key]

    def clear_overrides(self):
        """Clear all runtime overrides"""
        self._runtime_overrides.clear()

    def get_overrides_status(self) -> dict:
        """Get status of which settings have been overridden"""
        return {
            "HEAVY_MODEL_API_KEY": bool(
                self._runtime_overrides.get("HEAVY_MODEL_API_KEY")
            ),
            "LIGHT_MODEL_API_KEY": bool(
                self._runtime_overrides.get("LIGHT_MODEL_API_KEY")
            ),
            "CODING_MODEL_API_KEY": bool(
                self._runtime_overrides.get("CODING_MODEL_API_KEY")
            ),
            "IMAGE_GEN_API_KEY": bool(self._runtime_overrides.get("IMAGE_GEN_API_KEY")),
            "DEEPINFRA_API_KEY": bool(self._runtime_overrides.get("DEEPINFRA_API_KEY")),
            "DEVTO_API_KEY": bool(self._runtime_overrides.get("DEVTO_API_KEY")),
            "MISTRAL_API_KEY": bool(self._runtime_overrides.get("MISTRAL_API_KEY")),
        }

    # Properties to maintain compatibility
    @property
    def HEAVY_MODEL_API_KEY_CURRENT(self) -> str:
        return self.get_value("HEAVY_MODEL_API_KEY")

    @property
    def LIGHT_MODEL_API_KEY_CURRENT(self) -> str:
        return self.get_value("LIGHT_MODEL_API_KEY")

    @property
    def CODING_MODEL_API_KEY_CURRENT(self) -> str:
        return self.get_value("CODING_MODEL_API_KEY")

    @property
    def IMAGE_GEN_API_KEY_CURRENT(self) -> str:
        return self.get_value("IMAGE_GEN_API_KEY")

    @property
    def DEEPINFRA_API_KEY_CURRENT(self) -> str:
        return self.get_value("DEEPINFRA_API_KEY")

    @property
    def DEVTO_API_KEY_CURRENT(self) -> str:
        return self.get_value("DEVTO_API_KEY")

    @property
    def MISTRAL_API_KEY_CURRENT(self) -> str:
        return self.get_value("MISTRAL_API_KEY")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./scholarshare.db")

    # Application Settings
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "7860"))


settings = Settings()
