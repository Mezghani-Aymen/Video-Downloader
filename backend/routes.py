import uuid
from fastapi import APIRouter, BackgroundTasks
from schema import VideoRequest, DownloadRequest
from dependencies import VideoServiceDep

router = APIRouter(prefix="/api/video", tags=["Videos"])

@router.post("/info")
async def get_video_info(request: VideoRequest, service: VideoServiceDep):
    """Fetch available qualities, formats, and basic info for a given video URL."""
    return await service.get_video_info(request)

@router.post("/download")
async def download_video(
    request: DownloadRequest, 
    background_tasks: BackgroundTasks,
    service: VideoServiceDep
):
    """Trigger background download task."""
    task_id = str(uuid.uuid4())
    background_tasks.add_task(service.download_video_task, request, task_id)
    return {
        "message": "Download started successfully",
        "task_id": task_id,
        "status": "processing"
    }