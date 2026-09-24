from typing import Protocol, runtime_checkable
from schemas import VideoInfoResponse

@runtime_checkable
class IVideoExtractor(Protocol):
    """Interface for extracting metadata and available formats for a video URL."""
    async def extract_info(self, url: str) -> VideoInfoResponse:
        """Extract metadata and stream formats asynchronously."""
        ...
