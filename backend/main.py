from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from config import settings
from exceptions import (
    VideoProcessingError,
    VideoExtractionError,
    VideoDownloadError,
    DownloadTaskNotFoundError,
)
from logger import logger
from middleware import setup_middleware
from routes import router as video_router
from utils import setup_download_directory

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    setup_download_directory()
    try:
        import asyncio
        from dependencies import get_broadcaster
        broadcaster = get_broadcaster()
        if hasattr(broadcaster, "set_loop"):
            broadcaster.set_loop(asyncio.get_running_loop())
    except Exception as exc:
        logger.debug(f"Could not bind loop to broadcaster: {exc}")
    yield
    # Shutdown
    logger.info("Shutting down application")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

# Setup middleware
setup_middleware(app)

# Global Domain Exception Handlers (decoupling domain errors from HTTP layer)
@app.exception_handler(VideoExtractionError)
async def extraction_error_handler(request: Request, exc: VideoExtractionError):
    logger.error(f"Extraction error on {request.url}: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message, "type": "ExtractionError"},
    )

@app.exception_handler(VideoDownloadError)
async def download_error_handler(request: Request, exc: VideoDownloadError):
    logger.error(f"Download error on {request.url}: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": exc.message, "type": "DownloadError"},
    )

@app.exception_handler(DownloadTaskNotFoundError)
async def task_not_found_handler(request: Request, exc: DownloadTaskNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.message, "type": "TaskNotFound"},
    )

@app.exception_handler(VideoProcessingError)
async def generic_processing_error_handler(request: Request, exc: VideoProcessingError):
    logger.error(f"Processing error on {request.url}: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message, "type": "ProcessingError"},
    )

# Include routers
app.include_router(video_router)