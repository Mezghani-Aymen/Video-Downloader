import threading
from typing import Dict, List, Optional
from interfaces.task_manager import ITaskManager, TaskStatusLiteral
from schemas import TaskStatusResponse

class MemoryTaskManager(ITaskManager):
    """Thread-safe in-memory task status manager with subtask tracking."""

    def __init__(self):
        self._tasks: Dict[str, TaskStatusResponse] = {}
        self._lock = threading.Lock()

    def create_task(
        self,
        task_id: str,
        url: str,
        format_id: str,
        parent_task_id: Optional[str] = None,
        download_dir: Optional[str] = None,
    ) -> TaskStatusResponse:
        with self._lock:
            task = TaskStatusResponse(
                task_id=task_id,
                url=url,
                format_id=format_id,
                status="queued",
                progress=0,
                parent_task_id=parent_task_id,
                download_dir=download_dir,
            )
            self._tasks[task_id] = task
            return task

    def update_task(
        self,
        task_id: str,
        status: Optional[TaskStatusLiteral] = None,
        progress: Optional[int] = None,
        title: Optional[str] = None,
        filename: Optional[str] = None,
        error: Optional[str] = None,
        speed: Optional[str] = None,
        eta: Optional[str] = None,
        downloaded_bytes: Optional[int] = None,
        total_bytes: Optional[int] = None,
        download_dir: Optional[str] = None,
    ) -> TaskStatusResponse:
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                task = TaskStatusResponse(
                    task_id=task_id,
                    url="",
                    format_id="",
                    status=status or "downloading",
                    progress=progress or 0,
                    title=title,
                    filename=filename,
                    error=error,
                    speed=speed,
                    eta=eta,
                    downloaded_bytes=downloaded_bytes,
                    total_bytes=total_bytes,
                    download_dir=download_dir,
                )
                self._tasks[task_id] = task
                return task

            updated_data = task.model_dump()
            if status is not None:
                updated_data["status"] = status
            if progress is not None:
                updated_data["progress"] = min(100, max(0, progress))
            if title is not None:
                updated_data["title"] = title
            if filename is not None:
                updated_data["filename"] = filename
            if error is not None:
                updated_data["error"] = error
            if speed is not None:
                updated_data["speed"] = speed
            if eta is not None:
                updated_data["eta"] = eta
            if downloaded_bytes is not None:
                updated_data["downloaded_bytes"] = downloaded_bytes
            if total_bytes is not None:
                updated_data["total_bytes"] = total_bytes
            if download_dir is not None:
                updated_data["download_dir"] = download_dir

            updated_task = TaskStatusResponse(**updated_data)
            self._tasks[task_id] = updated_task
            return updated_task

    def get_task(self, task_id: str) -> Optional[TaskStatusResponse]:
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return None

            # If this is a batch parent task, gather all subtasks
            subtasks = [t for t in self._tasks.values() if t.parent_task_id == task_id]
            if subtasks:
                task_copy = task.model_copy()
                task_copy.subtasks = subtasks
                return task_copy

            return task

    def list_tasks(self) -> List[TaskStatusResponse]:
        with self._lock:
            # Return top-level tasks (either standalone or batch parents)
            return list(self._tasks.values())
