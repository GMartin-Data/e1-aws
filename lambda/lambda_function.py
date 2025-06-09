import logging
import sys

# Configure basic logging for the lambda runtime environment
# These logs will automatically be sent to CloudWatch
# For this, we have to explicitely set up a StreamHandler for robustness

# Get the root logger and set its level
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
    logger.info("⚡  Lambda function 'e1-aws-excel-processor' invoked.")
    # Use %s for logging dynamic data to conform to Ruff G004 (deferred formatting)
    logger.info("📥  Received event: %s", event)
    logger.info("🎒  Context object: %s", context)  # Log context for debugging purposes if needed-

    return {"statusCode": 200, "body": "Hello from Lambda! Function executed successfully."}
