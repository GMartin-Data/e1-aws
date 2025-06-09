from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """
    Base settings class for the entire e1-aws application.
    Provides default configuration for loading environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore extra fields not defined in the model
        case_sensitive=False,
    )

    # Common settings that might be shared across components, if any.
    # For now, we will primarily define component-specific settings.

    # Example: Application environment (e.g., 'development', 'production')
    APP_ENV: str = "development"
