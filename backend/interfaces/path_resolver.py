from typing import Protocol, runtime_checkable, Optional
from pathlib import Path

@runtime_checkable
class IDownloadPathResolver(Protocol):
    """
    Protocol for managing, validating, and resolving media download storage locations.
    Adheres to Single Responsibility Principle (SRP) and Open/Closed Principle (OCP).
    """

    def get_default_directory(self) -> Path:
        """Returns the current server default download directory."""
        ...

    def resolve_download_directory(self, requested_path: Optional[str] = None) -> Path:
        """
        Validates, normalizes, and ensures the target download directory exists.
        Falls back to default directory if requested_path is empty or invalid.
        """
        ...

    def set_default_directory(self, path: str) -> Path:
        """Updates the default download directory after validation."""
        ...
