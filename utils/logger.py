"""PARTH AI logging, configured once for this named logger."""

import logging
import os
from config import LOG_FILE

log_path = os.path.abspath(os.fspath(LOG_FILE))
os.makedirs(os.path.dirname(log_path), exist_ok=True)
logger = logging.getLogger("ParthAI")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%d-%m-%Y %H:%M:%S",
    ))
    logger.addHandler(handler)


def log_info(message: str):
    logger.info(message)


def log_warning(message: str):
    logger.warning(message)


def log_error(message: str):
    logger.error(message)
