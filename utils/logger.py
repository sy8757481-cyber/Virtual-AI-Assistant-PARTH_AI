import logging
import os
from config import LOG_FILE

# Create logs directory if it doesn't exist
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S"
)

# Logger object
logger = logging.getLogger("ParthAI")


def log_info(message: str):
    """
    Log normal information.
    """
    logger.info(message)


def log_warning(message: str):
    """
    Log warning messages.
    """
    logger.warning(message)


def log_error(message: str):
    """
    Log error messages.
    """
    logger.error(message)