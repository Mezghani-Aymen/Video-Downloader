from typing import Annotated
from fastapi import Depends

from interfaces.extractor import IVideoExtractor
from interfaces.downloader import IVideoDownloader
from interfaces.task_manager import ITaskManager
from interfaces.broadcaster import ITaskBroadcaster
from interfaces.path_resolver import IDownloadPathResolver

from services.yt_dlp_extractor import YtDlpExtractor
from services.yt_dlp_downloader import YtDlpDownloader
from services.memory_task_manager import MemoryTaskManager
from services.download_path_resolver import DownloadPathResolver
from services.task_broadcaster import WebSocketBroadcaster
from services.video_service import VideoService

# Singleton instances across requests
_task_manager_instance = MemoryTaskManager()
_broadcaster_instance = WebSocketBroadcaster()
_path_resolver_instance = DownloadPathResolver()

def get_task_manager() -> ITaskManager:
    return _task_manager_instance

def get_broadcaster() -> ITaskBroadcaster:
    return _broadcaster_instance

def get_path_resolver() -> IDownloadPathResolver:
    return _path_resolver_instance

def get_video_extractor() -> IVideoExtractor:
    return YtDlpExtractor()

def get_video_downloader() -> IVideoDownloader:
    return YtDlpDownloader()

def get_video_service(
    extractor: Annotated[IVideoExtractor, Depends(get_video_extractor)],
    downloader: Annotated[IVideoDownloader, Depends(get_video_downloader)],
    task_manager: Annotated[ITaskManager, Depends(get_task_manager)],
    path_resolver: Annotated[IDownloadPathResolver, Depends(get_path_resolver)],
    broadcaster: Annotated[ITaskBroadcaster, Depends(get_broadcaster)],
) -> VideoService:
    return VideoService(
        extractor=extractor,
        downloader=downloader,
        task_manager=task_manager,
        path_resolver=path_resolver,
        broadcaster=broadcaster,
    )

VideoServiceDep = Annotated[VideoService, Depends(get_video_service)]
TaskManagerDep = Annotated[ITaskManager, Depends(get_task_manager)]
PathResolverDep = Annotated[IDownloadPathResolver, Depends(get_path_resolver)]
BroadcasterDep = Annotated[ITaskBroadcaster, Depends(get_broadcaster)]