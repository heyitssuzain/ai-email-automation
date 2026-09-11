from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


# ============================================================
# LOG DIRECTORY
# ============================================================

LOG_DIR = Path("logs")
LOG_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

LOG_FILE = LOG_DIR / "app.log"


# ============================================================
# LOG FORMAT
# ============================================================

LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)s | "
    "%(name)s | "
    "%(message)s"
)


DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


# ============================================================
# LOGGING SETUP
# ============================================================

def setup_logging() -> None:

    root_logger = logging.getLogger()

    # Prevent duplicate handlers if setup_logging()
    # is called more than once.
    if root_logger.handlers:
        return

    root_logger.setLevel(
        logging.INFO
    )

    formatter = logging.Formatter(
        fmt=LOG_FORMAT,
        datefmt=DATE_FORMAT,
    )

    # --------------------------------------------------------
    # Console Handler
    # --------------------------------------------------------

    console_handler = logging.StreamHandler()

    console_handler.setLevel(
        logging.INFO
    )

    console_handler.setFormatter(
        formatter
    )

    # --------------------------------------------------------
    # Rotating File Handler
    # --------------------------------------------------------

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )

    file_handler.setLevel(
        logging.INFO
    )

    file_handler.setFormatter(
        formatter
    )

    # --------------------------------------------------------
    # Register handlers
    # --------------------------------------------------------

    root_logger.addHandler(
        console_handler
    )

    root_logger.addHandler(
        file_handler
    )


# ============================================================
# INITIALIZE
# ============================================================

setup_logging()