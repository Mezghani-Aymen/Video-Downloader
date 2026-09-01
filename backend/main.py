import os
from fastapi import FastAPI
from middleware import setup_middleware
from utils import setup_download_directory
from routes import router as video_router

app = FastAPI(title="Video Downloader API")

# Initialize setup and middleware
setup_middleware(app)

# Ensure download directory exists
setup_download_directory()

# Include routers
app.include_router(video_router)