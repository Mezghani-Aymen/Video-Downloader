from typing import Optional
from pathlib import Path
import imageio_ffmpeg
import yt_dlp

from config import settings
from exceptions import VideoDownloadError
from interfaces.downloader import IVideoDownloader, ProgressCallback
from logger import logger
from schemas import DownloadRequest
from services.youtube_auth import get_ydl_auth_opts

class YtDlpDownloader(IVideoDownloader):
    """Concrete media downloader using yt-dlp and ffmpeg."""

    def __init__(self, download_dir: Optional[Path] = None):
        self.download_dir = download_dir or settings.DOWNLOAD_DIR
        self.download_dir.mkdir(parents=True, exist_ok=True)

    def _resolve_ffmpeg(self) -> str:
        try:
            return imageio_ffmpeg.get_ffmpeg_exe()
        except Exception as exc:
            logger.warning(f"Could not locate imageio_ffmpeg binary: {exc}")
            return "ffmpeg"

    def download(
        self,
        request: DownloadRequest,
        task_id: str,
        on_progress: Optional[ProgressCallback] = None,
        output_dir: Optional[Path] = None,
    ) -> str:
        target_dir = output_dir or self.download_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        ffmpeg_path = self._resolve_ffmpeg()
        
        # Determine output filename template
        filename_prefix = f"%(title)s_{task_id}"
        if request.custom_filename:
            # Strip dangerous characters
            safe_custom_name = "".join(
                c for c in request.custom_filename if c.isalnum() or c in (" ", "-", "_")
            ).strip()
            if safe_custom_name:
                filename_prefix = f"{safe_custom_name}_{task_id}"

        output_template = str(target_dir / f"{filename_prefix}.%(ext)s")

        is_audio_only = request.format_id.lower() in ("audio_only", "ba", "bestaudio")
        format_spec = "bestaudio/best" if is_audio_only else f"{request.format_id}+bestaudio/best"

        ydl_opts = {
            "format": format_spec,
            "outtmpl": output_template,
            "ffmpeg_location": ffmpeg_path,
            "merge_output_format": settings.DEFAULT_AUDIO_FORMAT if is_audio_only else settings.DEFAULT_MERGE_FORMAT,
            "quiet": True,
            "no_warnings": True,
            # Merge anti-bot auth opts (PO token, visitor_data, User-Agent spoofing)
            **get_ydl_auth_opts(),
        }

        if request.download_subs:
            subs_lang = getattr(request, "subs_lang", "en") or "en"
            ydl_opts.update({
                "writesubtitles": True,
                "writeautomaticsub": True,
                "subtitleslangs": [subs_lang, "all"],
                "embedsubtitles": True,
                # Ensure the container supports embedding (mp4 does natively)
                "postprocessors": [
                    {
                        "key": "FFmpegEmbedSubtitle",
                        "already_have_subtitle": False,
                    }
                ],
            })

        if on_progress:
            def hook(d):
                status = d.get("status")
                if status == "downloading":
                    total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                    downloaded = d.get("downloaded_bytes", 0)
                    percent = int((downloaded / total_bytes) * 100) if total_bytes > 0 else 0
                    speed_str = d.get("_speed_str", "") or ""
                    eta_str = d.get("_eta_str", "") or ""
                    try:
                        on_progress(percent, speed_str, eta_str, downloaded, total_bytes)
                    except TypeError:
                        try:
                            on_progress(percent, speed_str)
                        except TypeError:
                            on_progress(percent)
                elif status == "finished":
                    try:
                        on_progress(100, "0 KB/s", "00:00", 0, 0)
                    except TypeError:
                        try:
                            on_progress(100, "0 KB/s")
                        except TypeError:
                            on_progress(100)

            ydl_opts["progress_hooks"] = [hook]

        try:
            logger.info(f"Starting download task {task_id} for URL: {request.url} into {target_dir}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(request.url, download=True)
                downloaded_file = ydl.prepare_filename(info_dict)
                logger.info(f"Task {task_id} successfully saved to {downloaded_file}")
                return downloaded_file
        except Exception as exc:
            logger.error(f"Download failed for task {task_id}: {exc}")
            raise VideoDownloadError(f"Download task {task_id} failed: {str(exc)}") from exc
