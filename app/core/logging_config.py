import logging

logger = logging.getLogger("liquor_store_logger")
logger.setLevel(logging.INFO)

# Stream handler (console output)
stream_handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
stream_handler.setFormatter(formatter)

# Prevent duplicate handlers in reload/debug mode
if not logger.handlers:
    logger.addHandler(stream_handler)
