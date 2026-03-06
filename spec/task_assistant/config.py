"""Configuration management for the Task Management Assistant."""

from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from .exceptions import ConfigurationError


class Settings(BaseSettings):
    """Application configuration from environment variables.
    
    Loads configuration from .env file using Pydantic settings.
    Validates required fields and provides defaults for optional ones.
    """
    
    openrouter_api_key: str = Field(
        ...,
        description="OpenRouter API key for AI provider authentication"
    )
    task_file_path: str = Field(
        default="tasks.md",
        description="Path to the markdown file for task storage"
    )
    default_model: str = Field(
        default="openrouter/free",
        description="OpenRouter model identifier to use for AI operations"
    )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


def load_config() -> Settings:
    """Load and validate configuration from environment variables.
    
    Reads configuration from .env file and validates all required fields.
    Provides descriptive error messages if configuration is invalid.
    
    Returns:
        Settings: Validated configuration object
        
    Raises:
        ConfigurationError: If configuration validation fails with descriptive message
    """
    try:
        return Settings()
    except ValidationError as e:
        # Extract field-specific error messages
        error_messages = []
        for error in e.errors():
            field = error['loc'][0] if error['loc'] else 'unknown'
            msg = error['msg']
            error_messages.append(f"  - {field}: {msg}")
        
        # Create descriptive error message
        error_detail = "\n".join(error_messages)
        raise ConfigurationError(
            f"Configuration validation failed:\n{error_detail}\n\n"
            f"Please ensure your .env file contains all required settings. "
            f"See .env.example for reference."
        ) from e
