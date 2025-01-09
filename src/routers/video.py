from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from src.services.video_service import download_video  # Import from services now

load_dotenv()
router = APIRouter()

class VideoDownloadRequest(BaseModel):                                              
    vimeo_url: str
    download_directory: str = "data/input/videos"

@router.post("/download", summary="Download Vimeo Video", tags=["Videos"])
def download_video_endpoint(request: VideoDownloadRequest):
    access_token = os.getenv("VIMEO_ACCESS_TOKEN")
    if not access_token:
        raise HTTPException(status_code=500, detail="Vimeo Access Token is missing.")
    
    try:
        file_path = download_video(request.vimeo_url, request.download_directory, access_token)
        return {"message": "Video downloaded successfully", "file_path": file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
