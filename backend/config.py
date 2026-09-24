from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional
import os

@dataclass
class Settings:
    PROJECT_NAME: str = "Video Downloader API"
    VERSION: str = "1.0.0"
    
    # Base paths
    BASE_DIR: Path = field(default_factory=lambda: Path(__file__).resolve().parent)
    DOWNLOAD_DIR: Path = field(
        default_factory=lambda: Path(
            os.getenv("DOWNLOAD_DIR", str(Path(__file__).resolve().parent.parent / "downloads"))
        )
    )
    
    # CORS
    ALLOWED_ORIGINS: List[str] = field(
        default_factory=lambda: [
            origin.strip()
            for origin in os.getenv(
                "ALLOWED_ORIGINS",
                "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,*"
            ).split(",")
            if origin.strip()
        ]
    )
    
    # yt-dlp / download configuration
    DEFAULT_MERGE_FORMAT: str = "mp4"
    DEFAULT_AUDIO_FORMAT: str = "mp3"
    MAX_FILESIZE_BYTES: int = 1024 * 1024 * 1024 * 2  # 2 GB limit

    # YouTube anti-bot authentication
    # Path to a Netscape-format cookies.txt exported from a logged-in browser.
    # Set the YOUTUBE_COOKIES_FILE env var on Render to enable cookie-based auth.
    YOUTUBE_COOKIES_FILE: Optional[str] = field(
        default_factory=lambda: os.getenv("YOUTUBE_COOKIES_FILE", "") or None
    )
    # How long (seconds) to cache PO tokens before re-generating them.
    PO_TOKEN_CACHE_TTL: int = field(
        default_factory=lambda: int(os.getenv("PO_TOKEN_CACHE_TTL", "600"))
    )
    
    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        self.DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


settings = Settings()
