from schema import VideoRequest, DownloadRequest
import yt_dlp 
from fastapi import HTTPException
import os
import imageio_ffmpeg

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

class VideoService:
    
    @staticmethod
    async def get_video_info(request: VideoRequest):
        ydl_opts = {}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(request.url, download=False)
                
                formats = []
                for f in info.get('formats', []):
                    # We filter to extract only relevant data for the frontend to show
                    # Some formats might be audio-only or video-only.
                    formats.append({
                        'format_id': f.get('format_id'),
                        'ext': f.get('ext'),
                        'resolution': f.get('resolution', 'audio only' if f.get('vcodec') == 'none' else 'unknown'),
                        'vcodec': f.get('vcodec'),
                        'acodec': f.get('acodec'),
                        'filesize': f.get('filesize') or f.get('filesize_approx')
                    })
                
                return {
                    "title": info.get('title'),
                    "thumbnail": info.get('thumbnail'),
                    "duration": info.get('duration'),
                    "formats": formats
                }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    def download_video_task(request: DownloadRequest, task_id: str):
        """
        Background task to download the video without blocking the API response.
        """
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        
        ydl_opts = {
            'format': f'{request.format_id}+bestaudio/best',
            'outtmpl': f'{DOWNLOAD_DIR}/%(title)s_{task_id}.%(ext)s',
            'ffmpeg_location': ffmpeg_path,
            'merge_output_format': 'mp4',
        }
        
        if request.download_subs:
            ydl_opts['writesubtitles'] = True
            ydl_opts['writeautomaticsub'] = True
            ydl_opts['subtitleslangs'] = ['en', 'all'] # Download English and all available subtitles
            ydl_opts['embedsubtitles'] = True # Embed them in the mp4/mkv

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([request.url])
        except Exception as e:
            print(f"Download task {task_id} failed: {e}")