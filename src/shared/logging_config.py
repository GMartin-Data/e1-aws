import logging
import os
from logging.handlers import RotatingFileHandler

from pythonjsonlogger.json import JsonFormatter


def setup_logging(
    log_level: str = "INFO",
    log_file: str = "logs/application.jsonl",
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,  # Keep 5 backup files
) -> None:
    """
    Configure the root logger to output logs to both console and a rotating file.

    Args:
        log_level (str): The minimum logging level (e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
        log_file (str): The path to the log file.
        max_bytes (int): The maximum size of the log file before it rotates.
        backup_count (int): The number of backup log files to keep.

    """
    # Ensure the log directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers to prevent duplicate logs if called multiple times
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Define JSON formatter
    json_formatter = JsonFormatter()

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )  # Simple text format for console
    root_logger.addHandler(console_handler)

    # File handler (rotating)
    file_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
    file_handler.setFormatter(json_formatter)
    root_logger.addHandler(file_handler)

    # Suppress noisy loggers from third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("SQLAlchemy").setLevel(logging.WARNING)
    logging.getLogger("pydantic_settings").setLevel(logging.WARNING)

    logging.info(r"ℹ️  Logging configured successfully to level: %s, file: %s", log_level, log_file)
