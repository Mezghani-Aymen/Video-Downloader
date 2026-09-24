import uuid
from typing import Optional, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from interfaces.extractor import IVideoExtractor
from interfaces.downloader import IVideoDownloader
from interfaces.task_manager import ITaskManager
from interfaces.path_resolver import IDownloadPathResolver
from interfaces.broadcaster import ITaskBroadcaster
from logger import logger
from schemas import (
    VideoRequest,
    DownloadRequest,
    DynamicDownloadRequest,
    VideoInfoResponse,
    TaskStatusResponse,
)

class VideoService:
    """
    Facade orchestrator coordinating extraction, dynamic downloading, and task management.
    Follows SRP, OCP, LSP, ISP, and DIP.
    """

    def __init__(
        self,
        extractor: IVideoExtractor,
        downloader: IVideoDownloader,
        task_manager: ITaskManager,
        path_resolver: Optional[IDownloadPathResolver] = None,
        broadcaster: Optional[ITaskBroadcaster] = None,
    ):
        self.extractor = extractor
        self.downloader = downloader
        self.task_manager = task_manager
        self.path_resolver = path_resolver
        self.broadcaster = broadcaster

    def _publish_update(self, task: TaskStatusResponse) -> None:
        """Broadcasts real-time task update to WebSocket listeners simultaneously."""
        if self.broadcaster:
            try:
                self.broadcaster.broadcast_sync(task.model_dump())
            except Exception as exc:
                logger.debug(f"Broadcaster notification error: {exc}")

    async def get_video_info(self, request: VideoRequest) -> VideoInfoResponse:
        """Fetch metadata and available qualities for a given video URL."""
        logger.info(f"Extracting video information for: {request.url}")
        return await self.extractor.extract_info(request.url)

    def download_video_task(self, request: DownloadRequest, task_id: str) -> None:
        """
        Standard single video download worker.
        Resolves custom directory and broadcasts live progress simultaneously.
        """
        output_dir = None
        if self.path_resolver:
            output_dir = self.path_resolver.resolve_download_directory(request.download_dir)

        task = self.task_manager.update_task(
            task_id,
            status="downloading",
            progress=5,
            download_dir=str(output_dir) if output_dir else None,
        )
        self._publish_update(task)

        def on_progress(percent: int, speed: str = "", eta: str = "", downloaded: int = 0, total: int = 0) -> None:
            updated = self.task_manager.update_task(
                task_id,
                progress=percent,
                speed=speed,
                eta=eta,
                downloaded_bytes=downloaded,
                total_bytes=total,
            )
            self._publish_update(updated)

        try:
            downloaded_path = self.downloader.download(
                request=request,
                task_id=task_id,
                on_progress=on_progress,
                output_dir=output_dir,
            )
            completed_task = self.task_manager.update_task(
                task_id,
                status="completed",
                progress=100,
                filename=downloaded_path,
                speed="0 KB/s",
            )
            self._publish_update(completed_task)
            logger.info(f"Task {task_id} marked completed.")
        except Exception as exc:
            logger.error(f"Task {task_id} failed with error: {exc}")
            failed_task = self.task_manager.update_task(
                task_id,
                status="failed",
                error=str(exc),
                speed="0 KB/s",
            )
            self._publish_update(failed_task)

    def download_dynamic_task(
        self,
        request: DynamicDownloadRequest,
        task_id: str,
        subtask_ids: Optional[List[str]] = None,
    ) -> None:
        """
        Dynamic download worker: transparently processes solo link or multi-link batch.
        Demonstrates Open/Closed Principle and Polymorphism.
        """
        urls = request.get_urls()
        if not urls:
            failed_task = self.task_manager.update_task(
                task_id,
                status="failed",
                error="No valid URLs provided to download.",
            )
            self._publish_update(failed_task)
            return

        # Solo link path
        if len(urls) == 1:
            single_request = DownloadRequest(
                url=urls[0],
                format_id=request.format_id,
                download_subs=request.download_subs,
                custom_filename=request.custom_filename,
                download_dir=request.download_dir,
            )
            self.download_video_task(single_request, task_id)
            return

        # Multi-link / Batch path
        output_dir = None
        if self.path_resolver:
            output_dir = self.path_resolver.resolve_download_directory(request.download_dir)

        # Update parent task to downloading
        parent_task = self.task_manager.update_task(
            task_id,
            status="downloading",
            progress=0,
            download_dir=str(output_dir) if output_dir else None,
        )
        self._publish_update(parent_task)

        # Map each URL to a subtask
        child_ids = subtask_ids or [str(uuid.uuid4()) for _ in urls]
        total_items = len(urls)
        subtask_progress: dict[str, int] = {cid: 0 for cid in child_ids}

        def execute_subtask(index: int, item_url: str, sub_id: str):
            sub_req = DownloadRequest(
                url=item_url,
                format_id=request.format_id,
                download_subs=request.download_subs,
                custom_filename=None,
                download_dir=request.download_dir,
            )

            # Mark subtask downloading
            sub_task = self.task_manager.update_task(
                sub_id,
                status="downloading",
                progress=5,
                download_dir=str(output_dir) if output_dir else None,
            )
            self._publish_update(sub_task)

            def on_sub_progress(percent: int, speed: str = "", eta: str = "", downloaded: int = 0, total: int = 0):
                subtask_progress[sub_id] = percent
                updated_sub = self.task_manager.update_task(
                    sub_id,
                    progress=percent,
                    speed=speed,
                    eta=eta,
                    downloaded_bytes=downloaded,
                    total_bytes=total,
                )
                self._publish_update(updated_sub)

                # Recompute aggregate batch progress
                overall_progress = int(sum(subtask_progress.values()) / total_items)
                updated_parent = self.task_manager.update_task(
                    task_id,
                    progress=overall_progress,
                )
                self._publish_update(updated_parent)

            try:
                filepath = self.downloader.download(
                    request=sub_req,
                    task_id=sub_id,
                    on_progress=on_sub_progress,
                    output_dir=output_dir,
                )
                subtask_progress[sub_id] = 100
                completed_sub = self.task_manager.update_task(
                    sub_id,
                    status="completed",
                    progress=100,
                    filename=filepath,
                    speed="0 KB/s",
                )
                self._publish_update(completed_sub)
                return True
            except Exception as exc:
                logger.error(f"Batch item {sub_id} failed: {exc}")
                subtask_progress[sub_id] = 100
                failed_sub = self.task_manager.update_task(
                    sub_id,
                    status="failed",
                    error=str(exc),
                    speed="0 KB/s",
                )
                self._publish_update(failed_sub)
                return False

        max_workers = min(request.concurrent_limit, total_items)
        success_count = 0
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_id = {
                executor.submit(execute_subtask, idx, url, cid): cid
                for idx, (url, cid) in enumerate(zip(urls, child_ids))
            }
            for future in as_completed(future_to_id):
                if future.result():
                    success_count += 1

        final_status = "completed" if success_count > 0 else "failed"
        final_parent = self.task_manager.update_task(
            task_id,
            status=final_status,
            progress=100,
            title=f"Batch: {success_count}/{total_items} items downloaded",
            speed="0 KB/s",
        )
        self._publish_update(final_parent)
        logger.info(f"Batch task {task_id} finished with {success_count}/{total_items} successful.")

    def get_task_status(self, task_id: str) -> Optional[TaskStatusResponse]:
        """Query the status of an ongoing or completed task."""
        return self.task_manager.get_task(task_id)
