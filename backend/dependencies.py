from typing import Annotated
from fastapi import Depends
from services import VideoService

def get_video_service() -> VideoService:
    return VideoService()

VideoServiceDep = Annotated[VideoService, Depends(get_video_service)]