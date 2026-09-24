import asyncio
from typing import Dict, Any, List
import yt_dlp

from exceptions import VideoExtractionError
from interfaces.extractor import IVideoExtractor
from logger import logger
from schemas import VideoInfoResponse, VideoFormatResponse
from services.youtube_auth import get_ydl_auth_opts

class YtDlpExtractor(IVideoExtractor):
    """Concrete video extractor using yt-dlp library."""

    def __init__(self, ydl_opts: Dict[str, Any] = None):
        base_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
        }
        # Merge anti-bot auth opts (PO token, visitor_data, User-Agent spoofing)
        auth_opts = get_ydl_auth_opts()
        self.ydl_opts = ydl_opts or {**base_opts, **auth_opts}

    def _sync_extract(self, url: str) -> Dict[str, Any]:
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info is None:
                    raise VideoExtractionError(f"No media information could be extracted for {url}")
                return info
        except Exception as exc:
            logger.error(f"Extraction failed for {url}: {exc}")
            raise VideoExtractionError(f"Extraction error: {str(exc)}") from exc

    async def extract_info(self, url: str) -> VideoInfoResponse:
        """Asynchronously extract video info without blocking the event loop."""
        info = await asyncio.to_thread(self._sync_extract, url)

        formats: List[VideoFormatResponse] = []
        raw_formats = info.get("formats", [])

        for f in raw_formats:
            format_id = f.get("format_id")
            if not format_id:
                continue

            vcodec = f.get("vcodec")
            acodec = f.get("acodec")
            is_audio_only = vcodec == "none" and acodec != "none"
            resolution = f.get("resolution") or ("audio only" if is_audio_only else "unknown")

            formats.append(
                VideoFormatResponse(
                    format_id=str(format_id),
                    ext=f.get("ext", "mp4"),
                    resolution=resolution,
                    vcodec=vcodec,
                    acodec=acodec,
                    filesize=f.get("filesize") or f.get("filesize_approx"),
                    note=f.get("format_note"),
                )
            )

        return VideoInfoResponse(
            title=info.get("title", "Untitled Video"),
            thumbnail=info.get("thumbnail"),
            duration=info.get("duration"),
            uploader=info.get("uploader"),
            views=info.get("view_count"),
            formats=formats,
            url=url,
        )
