from pydantic import BaseModel

# Request schemas
class VideoRequest(BaseModel):
    url: str

class DownloadRequest(BaseModel):
    url: str
    format_id: str  # The specific quality ID chosen by the user
    download_subs: bool = False
