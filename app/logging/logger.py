"""
Logging Setup
=============
Configures a rotating file logger + a colored console logger.
Import `logger` anywhere in the app: from app.logging.logger import logger
"""

import logging
import os
from logging.handlers import RotatingFileHandler

# Make sure the logs directory exists
os.makedirs("logs", exist_ok=True)

# ── Create the main application logger ───────────────────────────────────────
logger = logging.getLogger("ecommerce")
logger.setLevel(logging.DEBUG)

# ── Formatter ─────────────────────────────────────────────────────────────────
# Same format is applied to both file and console handlers
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

# ── File Handler ──────────────────────────────────────────────────────────────
# Rotates when the file hits 5 MB, keeps the last 3 backups
file_handler = RotatingFileHandler(
    "logs/app.log",
    maxBytes=5 * 1024 * 1024,  # 5 MB
    backupCount=3,
    encoding="utf-8",
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# ── Console Handler ───────────────────────────────────────────────────────────
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# ── Attach handlers (only once) ───────────────────────────────────────────────
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
