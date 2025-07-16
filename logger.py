import logging

# Global logger instance
logger = logging.getLogger("app_logger")

def configure_logger(debug_mode=False):
    """
    Configure the global logger.

    :param debug_mode: True to enable debug mode, False otherwise.
    """
    # Set log level
    if debug_mode:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Configure the logger handler
    handler = logging.StreamHandler()  # Log to console
    formatter = logging.Formatter('%(levelname)s - %(message)s')  # Simplified format
    handler.setFormatter(formatter)

    # Add the handler to the logger (avoid duplicates)
    if not logger.hasHandlers():
        logger.addHandler(handler)

# Logging functions
def debug(message):
    """Log a debug message."""
    logger.debug(message)

configure_logger(debug_mode=False)