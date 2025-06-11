import json
import logging
import os
import sys

import boto3
import pandas as pd
from sqlalchemy.orm import Session  # Type-hinting

from src.data_ingestion.settings import DataIngestionSettings
from src.data_ingestion.database import init_db, get_db
from src.data_ingestion.models import Communaute, Domaine, DataTable, DataColonne


# --- LOGGING SETUP ---
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Clear existing handlers to prevent duplicate logs if this setup runs multiple times
if logger.hasHandlers():
    logger.handlers.clear()

# Create a StreamHandler that directs logs to sys.stdout, which AWS Lambda captures for CloudWatch
console_handler = logging.StreamHandler(sys.stdout)

# Define a formatter for these logs (standard format)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)

# Add the handler to the root logger
logger.addHandler(console_handler)

# Finally, get a named logger for this specific module
logger = logging.getLogger(__name__)


# --- INITIALIZE GLOBAL SETTINGS AND S3 CLIENT ---
# Good practise to load settings outside the handler if they don't change per invocation
# This reduces cold start time
try:
    lambda_settings = DataIngestionSettings()  # type: ignore [reportCallIssue]
    logger.info("⚙️ Lambda settings loaded successfully from environment.")
except Exception as e:
    logger.exception("❌ Failed to load Lambda settings. This is critical.")
    # If settings cannot be loaded, the function cannot proceed.
    # For Lambda, raising an exception will indicate a failed invocation.
    raise RuntimeError("Failed to load Lambda settings.") from e

# Initialize S3 client globally
try:
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=lambda_settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=lambda_settings.AWS_SECRET_ACCESS_KEY.get_secret_value(),
        region_name=lambda_settings.AWS_REGION,
    )
    logger.info("☁️ S3 client initialized for region: %s", lambda_settings.AWS_REGION)
except Exception as e:
    logger.exception("❌ Failed to initialize S3 client. This is critical.")
    raise RuntimeError("Failed to initialize S3 client.") from e
# --- END GLOBAL INITIALIZATION ---


def lambda_handler(event: dict, context: object) -> dict:
    """
    Define a basic AWS Lambda function handler.

    This function is the entry point for Lambda invocations.
    It logs the incoming event and returns a simple success response.

    Args:
        event (dict): The event data that triggered the Lambda function.
                      For S3 triggers, this dict will contain details about
                      the uploaded object (e.g., bucket name, object key).
        context (object): The Lambda runtime context object. Provides
                          information about the invocation, function, and environment.

    Returns:
        dict: A response dictionary, typically containing 'statusCode' and 'body'.

    """
    logger.info("⚡ Lambda function 'e1-aws-excel-processor' invoked.")
    logger.info("📥 Received event: %s", event)
    logger.info("🎒 Context object: %s", context)

    # Log S3 event details if available
    if "Records" not in event or not event["Records"]:
        logger.error("❌ Invalid S3 event structure: Missing 'Records' key.")
        return {"statusCode": 400, "body": "Invalid S3 event."}

    s3_event_record = event["Records"][0]
    if s3_event_record.get("eventSource") != "aws:s3":
        logger.error("❌ Event source is not S3. Skipping processing.")
        return {"statusCode": 200, "body": "Not an S3 event."}

    bucket_name = s3_event_record["s3"]["bucket"]["name"]
    object_key = s3_event_record["s3"]["object"]["key"]
    logger.info("📂 S3 event detected: Object '%s' in bucket '%s'", object_key, bucket_name)
    # --- END S3 Event Parsing ---

    # --- S3 File Download and Pandas Read Logic ---
    download_path = os.path.join("/tmp", os.path.basename(object_key))
    excel_df: pd.DataFrame = pd.DataFrame()  # Initialize empty DataFrame

    try:
        logger.info("⬇️ Downloading S3 object '%s' from bucket '%s' to '%s'", object_key, bucket_name, download_path)
        s3_client.download_file(bucket_name, object_key, download_path)
        logger.info("✅ S3 object downloaded successfully.")

        logger.info("📊 Reading Excel file '%s' into Pandas DataFrame...", download_path)
        excel_df = pd.read_excel(download_path)
        logger.info("✅ Excel file read into DataFrame. Rows: %d, Columns: %d", excel_df.shape[0], excel_df.shape[1])

        # --- PLACEHOLDER FOR CLEANING/FORMATTING LOGIC ---
        logger.info("🧹 Placeholder: Data cleaning and formatting would be applied here.")

        # --- Database Initialization and Basic ORM Insertion ---
        logger.info("🗄️ Starting database initialization (if needed) and ORM insertion...")

        # Initialize the database (creates DB and tables if they don't exist)
        try:
            init_db()
            logger.info("✅ Database initialization complete.")
        except Exception as e:
            logger.exception("❌ Database initialization failed. Cannot proceed with ingestion.")
            return {"statusCode": 500, "body": f"DB Initialization Failed: {e}"}

        # Get a database session and perform basic ORM insertion
        db_session: Session  # Type hint for the session object
        try:
            with get_db() as db_session:
                # Create a sample Communaute record based on the file being processed
                # This is a very basic example; full processing will be more complex.
                communaute_name = f"Communaute from {os.path.basename(object_key)}"

                # Check if Communaute already exists before adding (to avoid IntegrityError on re-runs)
                existing_communaute = db_session.query(Communaute).filter_by(nom=communaute_name).first()

                if not existing_communaute:
                    logger.info("➕ Creating sample Communaute: %s", communaute_name)
                    new_communaute = Communaute(nom=communaute_name, description=f"Auto-created from {object_key}")
                    db_session.add(new_communaute)
                    db_session.commit()  # Commit to persist
                    db_session.refresh(new_communaute)  # Refresh to get auto-generated ID
                    logger.info("✅ Sample Communaute created successfully: %s", new_communaute.id)
                else:
                    logger.info("⏩ Communaute '%s' already exists. Skipping creation.", communaute_name)
                    new_communaute = existing_communaute  # Use existing for linking if needed later

            logger.info("✔️ Basic ORM insertion test completed successfully.")

        except Exception as e:
            logger.exception("❌ Error during ORM insertion test: %s", e)
            # It's good practice to rollback on error in a real transaction block,
            # but with get_db() context, the session is already managed.
            return {"statusCode": 500, "body": f"ORM Insertion Failed: {e}"}
        # --- End NEW: Database Initialization and Basic ORM Insertion ---

    except s3_client.exceptions.NoSuchKey:
        logger.error("❌ S3 object '%s' not found in bucket '%s'.", object_key, bucket_name)
        return {"statusCode": 404, "body": f"S3 object '{object_key}' not found."}

    except Exception as e:
        logger.exception("❌ Error during S3 download or Excel reading for object '%s': %s", object_key, e)
        return {"statusCode": 500, "body": f"Processing failed: {e}"}

    finally:
        # Clean up the temporary download file from Lambda's /tmp directory
        if os.path.exists(download_path):
            os.remove(download_path)
            logger.info("🗑️ Temporary file '%s' deleted from /tmp.", download_path)
    # --- End S3 File Download and Pandas Read Logic ---

    return {"statusCode": 200, "body": "Hello from Lambda! Function executed successfully."}
