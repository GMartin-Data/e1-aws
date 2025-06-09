import logging

# Configure basic logging for the lambda runtime environment
# These logs will automatically be sent to CloudWatch
logging.basicConfig(level=logging.INFO)
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
    logger.info("🎒  Context object: %s", context)  # Log context for debugging purposes if needed

    return {"statusCode": 200, "body": "Hello from Lambda! Function executed successfully."}
