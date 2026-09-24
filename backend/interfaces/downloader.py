from typing import Protocol, runtime_checkable, Callable, Optional, Any
from pathlib import Path
from schemas import DownloadRequest

# Progress callback accepts percent, speed string, ETA string, downloaded bytes, total bytes
ProgressCallback = Callable[..., Any]

@runtime_checkable
class IVideoDownloader(Protocol):
    """Interface for downloading video media."""
    def download(
        self,
        request: DownloadRequest,
        task_id: str,
        on_progress: Optional[ProgressCallback] = None,
        output_dir: Optional[Path] = None,
    ) -> str:
        """
        Executes download and merges media according to request.
        Allows specifying a custom output_dir (Open/Closed Principle).
        Returns the output filepath or identifier.
        """
        ...
