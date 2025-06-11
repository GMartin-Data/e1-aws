import logging
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy_utils import create_database, database_exists

from src.data_ingestion.models import Base
from src.data_ingestion.settings import DataIngestionSettings
from src.shared.logging_config import setup_logging

# Initialize logging for this module
setup_logging(log_level="INFO", log_file="logs/database_module.jsonl")
logger = logging.getLogger(__name__)

# Load database settings from .env via pydantic-settings
try:
    db_settings = DataIngestionSettings()  # type: ignore [reportCallIssue]
    logger.info("⚙️  Database settings loaded successfully.")
except Exception as e:
    logger.exception("❌  Failed to load database settings. Exiting module setup.")
    raise e

# Construct the database URL for Mysql/MariaDB
# URL format: "mysql+pymysql://user:password@host:port/database"
DATABASE_URL = (
    "mysql+pymysql://"
    f"{db_settings.MYSQL_USER}:{db_settings.MYSQL_PASSWORD.get_secret_value()}@"
    f"{db_settings.MYSQL_HOST}:{db_settings.MYSQL_PORT}/{db_settings.MYSQL_DB}"
)
logger.debug(
    "🔗  Constructed Database URL: %s", DATABASE_URL.replace(db_settings.MYSQL_PASSWORD.get_secret_value(), "****")
)

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=False)  # True for verbose SQL logging

# Configure SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """
    Initialize the database: creates the database itself if it doesn't exist
    and then creates all tables defined in the models.
    """
    logger.info("⏳ Starting database initialization...")
    try:
        # Check if database exists. If not, create it.
        if not database_exists(engine.url):
            logger.info("➕ Database '%s' does not exist. Creating now...", db_settings.MYSQL_DB)
            create_database(engine.url)
            logger.info("✅ Database '%s' created successfully.", db_settings.MYSQL_DB)
        else:
            logger.info("✅ Database '%s' already exists.", db_settings.MYSQL_DB)

        # Create all tables defined in the models (if not already existing)
        logger.info("➕ Creating database tables if they don't exist...")
        Base.metadata.create_all(engine)
        logger.info("✅ Database tables creation process completed.")
        logger.info("🔗 Database initialization completed successfully.")

    except OperationalError as e:
        logger.exception("❌ OperationalError during database initialization: %s", e)
        logger.error("Please ensure MySQL/MariaDB server is running and accessible.")
        raise

    except Exception as e:
        logger.exception("❌ An unexpected error occurred during database initialization: %s", e)
        raise


@contextmanager
def get_db() -> Generator[Session, Any, None]:
    """
    Dependency for FastAPI or other contexts to get a database session.
    Ensures the session is closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        logger.debug("🔒 Database session closed.")
