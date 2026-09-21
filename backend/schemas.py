from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class VideoRequest(BaseModel):
    url: str = Field(..., description="Target video URL to extract or download")


class DownloadRequest(BaseModel):
    url: str = Field(..., description="Target video URL")
    format_id: str = Field(..., description="Selected format or quality ID")
    download_subs: bool = Field(default=False, description="Whether to embed subtitles")
    subs_lang: str = Field(default="en", description="Preferred subtitle language code (e.g. en, fr, ar)")
    custom_filename: Optional[str] = Field(default=None, description="Optional custom filename")
    download_dir: Optional[str] = Field(default=None, description="Target download directory on server")


class DynamicDownloadRequest(BaseModel):
    """
    Polymorphic download request accepting either a single URL or multiple URLs.
    Adheres to Open/Closed Principle and Interface Segregation Principle.
    """
    url: Optional[str] = Field(default=None, description="Target single video URL")
    urls: Optional[List[str]] = Field(default=None, description="List of target video URLs for batch download")
    format_id: str = Field(default="1080p", description="Selected format or quality ID")
    download_subs: bool = Field(default=False, description="Whether to embed subtitles")
    subs_lang: str = Field(default="en", description="Preferred subtitle language code")
    custom_filename: Optional[str] = Field(default=None, description="Optional custom filename (single link only)")
    download_dir: Optional[str] = Field(default=None, description="Target download directory on server")
    concurrent_limit: int = Field(default=3, ge=1, le=5, description="Max concurrent downloads for batch")

    def get_urls(self) -> List[str]:
        if self.urls and len(self.urls) > 0:
            return [u.strip() for u in self.urls if u.strip()]
        if self.url and self.url.strip():
            return [self.url.strip()]
        return []

    def is_batch(self) -> bool:
        return len(self.get_urls()) > 1


class BatchDownloadRequest(BaseModel):
    urls: List[str] = Field(..., min_length=1, description="List of target video URLs")
    format_id: str = Field(default="1080p", description="Selected format or quality ID")
    download_subs: bool = Field(default=False, description="Whether to embed subtitles")
    download_dir: Optional[str] = Field(default=None, description="Target download directory on server")
    concurrent_limit: int = Field(default=3, ge=1, le=5, description="Max concurrent downloads")


class VideoFormatResponse(BaseModel):
    format_id: str
    ext: str
    resolution: str
    vcodec: Optional[str] = None
    acodec: Optional[str] = None
    filesize: Optional[int] = None
    note: Optional[str] = None


class VideoInfoResponse(BaseModel):
    title: str
    thumbnail: Optional[str] = None
    duration: Optional[int] = None
    uploader: Optional[str] = None
    views: Optional[int] = None
    formats: List[VideoFormatResponse] = Field(default_factory=list)
    url: str


class DownloadTaskResponse(BaseModel):
    message: str
    task_id: str
    status: Literal["queued", "downloading", "completed", "failed"]
    subtask_ids: Optional[List[str]] = None


class TaskStatusResponse(BaseModel):
    task_id: str
    url: str
    format_id: str
    status: Literal["queued", "downloading", "completed", "failed"]
    progress: int = Field(default=0, ge=0, le=100)
    title: Optional[str] = None
    filename: Optional[str] = None
    error: Optional[str] = None
    speed: Optional[str] = None
    eta: Optional[str] = None
    downloaded_bytes: Optional[int] = None
    total_bytes: Optional[int] = None
    download_dir: Optional[str] = None
    parent_task_id: Optional[str] = None
    subtasks: Optional[List["TaskStatusResponse"]] = None


class SettingsConfigResponse(BaseModel):
    default_download_dir: str
    system_downloads_dir: str


class SettingsUpdateRequest(BaseModel):
    download_dir: str = Field(..., min_length=1, description="Target download directory to set as default")
