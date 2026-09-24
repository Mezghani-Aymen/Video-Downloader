import os
from pathlib import Path
from typing import Optional
from config import settings
from interfaces.path_resolver import IDownloadPathResolver
from logger import logger

class DownloadPathResolver(IDownloadPathResolver):
    """
    Concrete download path resolver following Single Responsibility Principle (SRP).
    Encapsulates path validation, security, platform normalization, and creation.
    """

    def __init__(self, default_dir: Optional[Path] = None):
        self._default_dir = default_dir or settings.DOWNLOAD_DIR
        self._default_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def get_system_downloads_directory() -> Path:
        """Returns the user OS default Downloads folder."""
        system_download = Path.home() / "Downloads"
        return system_download if system_download.exists() else Path.home()

    def get_default_directory(self) -> Path:
        """Returns the active default download directory."""
        return self._default_dir

    def resolve_download_directory(self, requested_path: Optional[str] = None) -> Path:
        """
        Validates, normalizes, and creates the target download directory.
        Falls back safely to the default directory if requested path cannot be created.
        """
        if not requested_path or not requested_path.strip():
            return self._default_dir

        try:
            expanded = os.path.expanduser(requested_path.strip())
            target_path = Path(expanded).resolve()

            # Create if it does not exist
            target_path.mkdir(parents=True, exist_ok=True)

            # Test writability by checking write permissions
            if not os.access(target_path, os.W_OK):
                logger.warning(
                    f"Requested directory '{target_path}' is not writable. Falling back to default '{self._default_dir}'."
                )
                return self._default_dir

            return target_path
        except Exception as exc:
            logger.warning(
                f"Invalid download directory '{requested_path}': {exc}. Falling back to default '{self._default_dir}'."
            )
            return self._default_dir

    def set_default_directory(self, path: str) -> Path:
        """Sets and validates a new default download directory."""
        resolved = self.resolve_download_directory(path)
        self._default_dir = resolved
        settings.DOWNLOAD_DIR = resolved
        logger.info(f"Default download directory updated to: {resolved}")
        return resolved
