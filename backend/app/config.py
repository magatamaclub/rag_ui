import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Get the project root directory (two levels up from this file)
project_root = Path(__file__).parent.parent.parent
env_file = project_root / ".env"

# Load environment variables from .env file
load_dotenv(env_file)


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self):
        # Database configuration
        self.DB_HOST: str = os.getenv("DB_HOST", "localhost")
        self.DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
        self.DB_NAME: str = os.getenv("DB_NAME", "rag_db")
        self.DB_USER: str = os.getenv("DB_USER", "user")
        self.DB_PASSWORD: str = os.getenv("DB_PASSWORD", "password")

        # Application configuration
        self.APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
        self.APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
        debug_env = os.getenv("APP_DEBUG", "false").lower()
        self.APP_DEBUG: bool = debug_env == "true"

        # JWT configuration
        self.SECRET_KEY: str = os.getenv(
            "SECRET_KEY", "your-secret-key-change-this-in-production"
        )
        self.ALGORITHM: str = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
        )

        # Default admin user configuration
        self.DEFAULT_ADMIN_USERNAME: str = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
        self.DEFAULT_ADMIN_EMAIL: str = os.getenv(
            "DEFAULT_ADMIN_EMAIL", "admin@example.com"
        )
        self.DEFAULT_ADMIN_PASSWORD: str = os.getenv(
            "DEFAULT_ADMIN_PASSWORD", "admin123"
        )

        # Logging configuration
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()

        # CORS configuration
        cors_origins = os.getenv("CORS_ORIGINS", "")
        self.CORS_ORIGINS: list = [
            origin.strip() for origin in cors_origins.split(",") if origin.strip()
        ]

        # Frontend configuration
        self.REACT_APP_API_BASE_URL: str = os.getenv("REACT_APP_API_BASE_URL", "")

        # Build database URL
        self._database_url: Optional[str] = os.getenv("DATABASE_URL")

    @property
    def DATABASE_URL(self) -> str:
        """Get database URL from environment or construct from components."""
        if self._database_url:
            return self._database_url
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


# Create global settings instance
settings = Settings()
