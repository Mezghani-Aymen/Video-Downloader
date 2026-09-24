from typing import Protocol, runtime_checkable, Optional, List, Literal
from schemas import TaskStatusResponse

TaskStatusLiteral = Literal["queued", "downloading", "completed", "failed"]

@runtime_checkable
class ITaskManager(Protocol):
    """Interface for managing background task statuses and progress."""
    def create_task(
        self,
        task_id: str,
        url: str,
        format_id: str,
        parent_task_id: Optional[str] = None,
        download_dir: Optional[str] = None,
    ) -> TaskStatusResponse:
        ...

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
        ...

    def get_task(self, task_id: str) -> Optional[TaskStatusResponse]:
        ...

    def list_tasks(self) -> List[TaskStatusResponse]:
        ...
