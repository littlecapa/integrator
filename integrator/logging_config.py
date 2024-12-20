import json
import logging
import os


# Custom formatter to handle missing operation gracefully
class CustomFormatter(logging.Formatter):
    def format(self, record):
        # Ensure 'operation' exists in the record, default to 'general'
        if not hasattr(record, 'operation'):
            record.operation = 'general'
        return super().format(record)

# Configure logging
def configure_logging(log_file_name="integrator.log"):
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, log_file_name)

    # Set up the logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create formatters with the custom formatter
    log_format = "%(asctime)s - %(levelname)s - %(operation)s - %(message)s"
    formatter = CustomFormatter(log_format)

    # Create handlers
    file_handler = logging.FileHandler(log_file_path)
    stream_handler = logging.StreamHandler()

    # Add formatter to handlers
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    logging.info("Logging configured successfully.")

# Log operation details
def log_operation(level, message, operation=None, **kwargs):
    logger = logging.getLogger()
    extra = {"operation": operation or "general"}

    if kwargs:
        message = f"{message} | Details: {json.dumps(kwargs)}"

    if level.lower() == "info":
        logger.info(message, extra=extra)
    elif level.lower() == "error":
        logger.error(message, extra=extra)
    elif level.lower() == "debug":
        logger.debug(message, extra=extra)
    else:
        logger.warning(message, extra=extra)
