import json
import logging
import os

from elasticsearch import Elasticsearch, helpers


# Custom formatter to handle missing attributes gracefully
class CustomFormatter(logging.Formatter):
    def format(self, record):
        # Ensure 'operation' and 'object' exist in the record, default to empty string
        record.operation = getattr(record, 'operation', '')
        record.object = getattr(record, 'object', '')
        
        # Omit operation and object if they are empty
        if not record.operation and not record.object:
            log_format = "%(asctime)s - %(levelname)s - %(message)s"
        else:
            log_format = "%(asctime)s - %(levelname)s - %(message)s - [Operation: %(operation)s | Object: %(object)s]"
        
        # Apply the format based on whether operation/object are empty or not
        formatter = logging.Formatter(log_format)
        return formatter.format(record)


# ELK Logging Handler
class ElkLoggingHandler(logging.Handler):
    def __init__(self, index_name, ip, port):
        super().__init__()
        self.index_name = index_name
        self.es = Elasticsearch([{'host': ip, 'port': port}])
    
    def emit(self, record):
        log_entry = self.format(record)
        try:
            # Index the log into Elasticsearch
            self.es.index(index=self.index_name, document=json.loads(log_entry))
        except Exception as e:
            logging.error(f"Failed to send log to Elasticsearch: {e}")

# Configure logging
def configure_logging(log_file_name="integrator.log"):
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, log_file_name)

    # Set up the logger
    logger = logging.getLogger()
    if not logger.hasHandlers():  # Prevent duplicate handlers
        logger.setLevel(logging.INFO)

        # Create formatters with the custom formatter
        formatter = CustomFormatter()

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
def log_operation(level, message, object=None, operation=None, **kwargs):
    logger = logging.getLogger()

    # Ensure `extra` contains required fields
    extra = {
        "operation": operation or "general",
        "object": object or "general",
    }

    # Append additional details to the message if provided
    if kwargs:
        message = f"{message} | Details: {json.dumps(kwargs)}"

    # Use dynamic level logging
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.log(log_level, message, extra=extra)


# Function to add ELK logging
def add_elk_logging(index_name, ip, port):
    elk_handler = ElkLoggingHandler(index_name, ip, port)
    formatter = CustomFormatter()
    elk_handler.setFormatter(formatter)
    
    # Add ELK handler to the logger
    logging.getLogger().addHandler(elk_handler)
    
    logging.info(f"ELK logging enabled for index '{index_name}' at {ip}:{port}")
