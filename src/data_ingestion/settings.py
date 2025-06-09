from pydantic import Field, SecretStr

from src.shared.settings import AppSettings


class DataIngestionSettings(AppSettings):
    """
    Settings for the Excel to MySQL data ingestion workflow.
    Loads AWS and MySQL database configuration.
    """

    # AWS Settings
    AWS_ACCESS_KEY_ID: str = Field(..., description="AWS Access Key ID")
    AWS_SECRET_ACCESS_KEY: SecretStr = Field(..., description="AWS Secret Access Key")
    AWS_REGION: str = Field(..., description="AWS Region for services")

    # MySQL Database Settings for RDS
    MYSQL_HOST: str = Field(..., description="MySQL database host")
    MYSQL_PORT: int = Field(3306, description="MySQL database port", ge=0, le=65535)
    MYSQL_USER: str = Field(..., description="MySQL database user")
    MYSQL_PASSWORD: SecretStr = Field(..., description="MySQL database password")
    MYSQL_DB: str = Field(..., description="MySQL database name")

    # S3
    S3_BUCKET_NAME: str = Field("e1-aws-59120", description="Name of the S3 bucket for Excel files")
