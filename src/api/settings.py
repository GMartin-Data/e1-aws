from typing import Literal

from pydantic import Field, SecretStr

from src.shared.settings import AppSettings


class APISettings(AppSettings):
    """
    Settings for the FastAPI application.
    Loads API configuration, including JWT secret.
    """

    # API Core Settings
    API_TITLE: str = "e1-aws REST API"
    API_DESCRIPTION: str = "API to interact with the Excel data stored in MySQL on AWS RDS."
    API_VERSION: str = "0.1.0"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = Field(8000, description="API server port", ge=0, le=65535)
    API_ENVIRONMENT: Literal["development", "production", "testing"] = "development"

    # JWT Authentication Settings
    JWT_SECRET_KEY: SecretStr = Field(..., description="Secret key for JWT encoding/decoding")
    JWT_ALGORITHM: str = Field("HS256", description="JWT algorithm for signing tokens (e.g., HS256). Avoid 'None'.")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, description="Access token expiration time in minutes")

    # Database Settings
    # Repeated for the sake of simplicity, as this is a separate module
    # NOTE: For production, consider loading this from a common source (e.g, AWS Secrets Manager)
    MYSQL_HOST: str = Field(..., description="MySQL database host")
    MYSQL_PORT: int = Field(3306, description="MySQL database port", ge=0, le=65535)
    MYSQL_USER: str = Field(..., description="MySQL database username")
    MYSQL_PASSWORD: SecretStr = Field(..., description="MySQL database password")
    MYSQL_DB: str = Field(..., description="MySQL database name")
