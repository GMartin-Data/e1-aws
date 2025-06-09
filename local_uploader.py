import hashlib
import logging
import os

import boto3
from botocore.client import BaseClient
from botocore.exceptions import ClientError

from src.data_ingestion.settings import DataIngestionSettings
from src.shared.logging_config import setup_logging

setup_logging(log_level="INFO", log_file="logs/local_uploader.jsonl")
logger = logging.getLogger(__name__)


def calculate_md5_etag(filepath: str) -> str:
    """
    Calculate the MD5 hash (ETag-like) of a file's content.
    For non-multipart S3 uploads, ETag is simply the MD5 hash of the object data.

    Args:
        filepath (str): The path to the local file.

    Returns:
        str: The MD5 hash in hexadecimal format.

    """
    hash_md5 = hashlib.md5()
    # Read file in chunks to handle large files efficiently
    with open(filepath, "rb") as read_file:
        for chunk in iter(lambda: read_file.read(4_096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def upload_file_to_s3(local_filepath: str, bucket_name: str, s3_prefix: str, s3_client: BaseClient) -> bool:
    """
    Upload a file to a specified S3 bucket and prefix.
    Checks if the file already exists in S3 and if its content has changed.

    Args:
        local_filepath (str): The full path to the local file (e.g., /path/to/my_file.xlsx).
        bucket_name (str): The name of the S3 bucket (e.g., 'e1-aws-59120').
        s3_prefix (str): The 'folder' prefix within the S3 bucket (e.g., 'raw/').
                         Must end with a '/'.
        s3_client (boto3.client): An initialized Boto3 S3 client.

    Returns:
        bool: True if the file was successfully uploaded or was already
              up-to-date, False otherwise (e.g., due to an S3 error).

    """
    filename = os.path.basename(local_filepath)
    s3_key = f"{s3_prefix}{filename}"

    try:
        # Try to get metadata of the S3 object
        # in order to check if it already exists in S3
        s3_object_metadata = s3_client.head_object(Bucket=bucket_name, Key=s3_key)
        s3_etag = s3_object_metadata.get("ETag", "").strip('"')  # S3's ETag

        local_etag = calculate_md5_etag(local_filepath)  # Our calculated local ETag

        if s3_etag == local_etag:
            logger.info("⏩  File already exists in S3 and is identical: %s", s3_key)
            return True  # File is already up-to-date
        else:
            logger.info("🔄  File exists in S3 but content has changed, Re-uploading: %s", s3_key)
            s3_client.upload_file(local_filepath, bucket_name, s3_key)
            logger.info("🆕  File re-uploaded successfully: %s", s3_key)
            return True

    except ClientError as e:
        # If head_object returns 404 (not found), the file does not exist in S3
        # Hence, we proceed to upload it
        if e.response["Error"]["Code"] == "404":
            logger.info("⬆️  Uploading new file: %s to s3://%s/%s", filename, bucket_name, s3_key)
            s3_client.upload_file(local_filepath, bucket_name, s3_key)
            logger.info("➕  File uploaded successfully: %s", s3_key)
            return True
        else:
            # Log other S3-related errors
            logger.exception("❌  S3 ClientError during upload for %s: %s", filename, e)
            return False

    except Exception as e:
        # Catch and log any other unexpected errors during the process
        logger.exception("❌  Unexpected error during upload for %s: %s", filename, e)
        return False


def main() -> None:
    """Orchestrate the local Excel file upload process to S3."""
    logger.info("🚀  Starting local Excel file upload process.")

    # Load application settings (including AWS credentials and S3 bucket name)
    settings = DataIngestionSettings()  # type: ignore

    # Initialize Boto3 S3 Client using credentials from settings
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY.get_secret_value(),
        region_name=settings.AWS_REGION,
    )

    local_files_folder = "local_excel_files"
    s3_upload_prefix = "raw/"

    if not os.path.exists(local_files_folder):
        logger.error("❌  Local files folder does not exist: %s", local_files_folder)
        return  # Exit if the folder does not exist

    uploaded_or_updated_count = 0
    skipped_count = 0
    failed_count = 0

    for filename in os.listdir(local_files_folder):
        if filename.endswith((".xlsx", ".xls")):
            local_filepath = os.path.join(local_files_folder, filename)
            logger.info("📄  Processing file: %s", local_filepath)

            if upload_file_to_s3(local_filepath, settings.S3_BUCKET_NAME, s3_upload_prefix, s3_client):
                uploaded_or_updated_count += 1
            else:
                failed_count += 1
        else:
            logger.warning("⏩  Skipping non-Excel file: %s", filename)
            skipped_count += 1

    logger.info("🏁 Upload process finished.")
    logger.info(
        "📋  Summary: Uploaded/Updated: %d, Skipped: %d, Failed: %d",
        uploaded_or_updated_count,
        skipped_count,
        failed_count,
    )


if __name__ == "__main__":
    main()
