from pathlib import Path
from config import settings
from logger import logger

def setup_download_directory() -> Path:
    """Ensure the configured download directory exists."""
    settings.ensure_directories()
    logger.info(f"Download directory verified at: {settings.DOWNLOAD_DIR}")
    return settings.DOWNLOAD_DIR