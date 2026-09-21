import uuid
from typing import List
from fastapi import APIRouter, BackgroundTasks, HTTPException, status, WebSocket, WebSocketDisconnect
from exceptions import DownloadTaskNotFoundError
from schemas import (
    VideoRequest,
    DownloadRequest,
    DynamicDownloadRequest,
    BatchDownloadRequest,
    VideoInfoResponse,
    DownloadTaskResponse,
    TaskStatusResponse,
    SettingsConfigResponse,
    SettingsUpdateRequest,
)
from dependencies import VideoServiceDep, TaskManagerDep, PathResolverDep, BroadcasterDep
from services.download_path_resolver import DownloadPathResolver

router = APIRouter(prefix="/api/video", tags=["Videos"])

@router.post("/info", response_model=VideoInfoResponse)
async def get_video_info(request: VideoRequest, service: VideoServiceDep):
    """Fetch available qualities, formats, and basic info for a given video URL."""
    return await service.get_video_info(request)

@router.post("/download", response_model=DownloadTaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def download_video(
    request: DynamicDownloadRequest,
    background_tasks: BackgroundTasks,
    service: VideoServiceDep,
    task_manager: TaskManagerDep,
):
    """
    Dynamic media download endpoint: handles either a solo link or multi-link batch seamlessly.
    Adheres to Open/Closed and Liskov Substitution principles.
    """
    urls = request.get_urls()
    if not urls:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one target video URL must be provided in 'url' or 'urls'.",
        )

    task_id = str(uuid.uuid4())

    if request.is_batch():
        # Create subtask IDs and register them with task_manager
        subtask_ids = [str(uuid.uuid4()) for _ in urls]
        task_manager.create_task(
            task_id=task_id,
            url=f"Batch: {len(urls)} items",
            format_id=request.format_id,
            download_dir=request.download_dir,
        )
        for sub_id, u in zip(subtask_ids, urls):
            task_manager.create_task(
                task_id=sub_id,
                url=u,
                format_id=request.format_id,
                parent_task_id=task_id,
                download_dir=request.download_dir,
            )

        background_tasks.add_task(
            service.download_dynamic_task,
            request,
            task_id,
            subtask_ids,
        )

        return DownloadTaskResponse(
            message=f"Batch download with {len(urls)} videos queued successfully",
            task_id=task_id,
            status="queued",
            subtask_ids=subtask_ids,
        )
    else:
        # Solo download
        task_manager.create_task(
            task_id=task_id,
            url=urls[0],
            format_id=request.format_id,
            download_dir=request.download_dir,
        )
        background_tasks.add_task(
            service.download_dynamic_task,
            request,
            task_id,
        )

        return DownloadTaskResponse(
            message="Download task queued successfully",
            task_id=task_id,
            status="queued",
        )

@router.post("/batch", response_model=DownloadTaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def download_batch(
    request: BatchDownloadRequest,
    background_tasks: BackgroundTasks,
    service: VideoServiceDep,
    task_manager: TaskManagerDep,
):
    """Explicit batch download endpoint for multi-link queues."""
    dynamic_req = DynamicDownloadRequest(
        urls=request.urls,
        format_id=request.format_id,
        download_subs=request.download_subs,
        download_dir=request.download_dir,
        concurrent_limit=request.concurrent_limit,
    )
    return await download_video(
        request=dynamic_req,
        background_tasks=background_tasks,
        service=service,
        task_manager=task_manager,
    )

@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str, service: VideoServiceDep):
    """Query progress and state of a background download task."""
    task = service.get_task_status(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task '{task_id}' not found.",
        )
    return task

@router.get("/tasks", response_model=List[TaskStatusResponse])
async def list_all_tasks(task_manager: TaskManagerDep):
    """List all registered download tasks."""
    return task_manager.list_tasks()

@router.get("/settings", response_model=SettingsConfigResponse)
async def get_download_settings(path_resolver: PathResolverDep):
    """Retrieve current configured server download directory and default system location."""
    return SettingsConfigResponse(
        default_download_dir=str(path_resolver.get_default_directory()),
        system_downloads_dir=str(DownloadPathResolver.get_system_downloads_directory()),
    )

@router.post("/settings", response_model=SettingsConfigResponse)
async def update_download_settings(
    payload: SettingsUpdateRequest,
    path_resolver: PathResolverDep,
):
    """Validate and update the default download directory."""
    updated_path = path_resolver.set_default_directory(payload.download_dir)
    return SettingsConfigResponse(
        default_download_dir=str(updated_path),
        system_downloads_dir=str(DownloadPathResolver.get_system_downloads_directory()),
    )

@router.websocket("/ws")
async def tasks_websocket_endpoint(
    websocket: WebSocket,
    broadcaster: BroadcasterDep,
    task_manager: TaskManagerDep,
):
    """
    Simultaneous real-time task progress synchronization WebSocket endpoint.
    Pushes live download speeds, ETAs, and completion statuses instantly to clients.
    """
    await broadcaster.connect(websocket)
    try:
        # Send initial snapshot of currently active tasks
        active_tasks = [
            t.model_dump() for t in task_manager.list_tasks()
            if t.status in ("queued", "downloading")
        ]
        if active_tasks:
            await websocket.send_json({"type": "snapshot", "tasks": active_tasks})

        while True:
            # Keep-alive loop listening for client heartbeat or pings
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        await broadcaster.disconnect(websocket)
    except Exception:
        await broadcaster.disconnect(websocket)