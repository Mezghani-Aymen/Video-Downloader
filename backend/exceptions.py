class VideoProcessingError(Exception):
    """Base exception for video processing domain errors."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class VideoExtractionError(VideoProcessingError):
    """Raised when extracting video metadata fails."""
    pass


class VideoDownloadError(VideoProcessingError):
    """Raised when downloading video content fails."""
    pass


class DownloadTaskNotFoundError(VideoProcessingError):
    """Raised when requested task ID does not exist."""
    def __init__(self, task_id: str):
        super().__init__(f"Download task '{task_id}' was not found.")
        self.task_id = task_id
