"""
Configuration module for the Todo API application.
Handles environment variable validation and settings.
"""

import os
import sys
from typing import Optional


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self):
        self.validate_required_vars()

    def validate_required_vars(self):
        """Validate required environment variables are set."""
        required_vars = [
            "DATABASE_URL",
            "SECRET_KEY",
            "ACCESS_TOKEN_EXPIRE_MINUTES"
        ]

        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            print(f"Error: Required environment variables are not set: {', '.join(missing_vars)}")
            print("Please set these variables in your environment or .env file.")
            sys.exit(1)

    @property
    def database_url(self) -> str:
        """Get the database URL from environment."""
        return os.getenv("DATABASE_URL")

    @property
    def secret_key(self) -> str:
        """Get the secret key from environment."""
        return os.getenv("SECRET_KEY")

    @property
    def access_token_expire_minutes(self) -> int:
        """Get the access token expiration time from environment."""
        try:
            return int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        except ValueError:
            print("Warning: ACCESS_TOKEN_EXPIRE_MINUTES is not a valid integer, using default value of 30")
            return 30

    @property
    def cors_allowed_origins(self) -> list:
        """Get the allowed CORS origins from environment."""
        cors_origins_str = os.getenv("CORS_ALLOWED_ORIGINS", "")
        cors_origins = [origin.strip() for origin in cors_origins_str.split(",") if origin.strip()]

        # Add GitHub Pages origin if not already included
        github_pages_origin = "https://mfsrajput.github.io"
        if github_pages_origin not in cors_origins:
            cors_origins.append(github_pages_origin)

        return cors_origins

    @property
    def environment(self) -> str:
        """Get the environment (development, production, etc.)"""
        return os.getenv("ENVIRONMENT", "development")


# Global settings instance
settings = Settings()