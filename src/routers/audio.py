from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.audio_service import extract_audio
from config import Config

router = APIRouter()

class AudioExtractionRequest(BaseModel):
    video_path: str
    output_directory: str = None

@router.post("/extract", summary="Extract audio from video", tags=["Audio"])
async def extract_audio_endpoint(request: AudioExtractionRequest):
    """
    Extracts MP3 audio from a video file.
    
    Args:
        request (AudioExtractionRequest): Request containing video path and optional output directory
        
    Returns:
        dict: Message indicating success and the output path
        
    Raises:
        HTTPException: If extraction fails
    """
    try:
        # Fallback to config if request.output_directory is None
        output_dir = request.output_directory or str(Config.TEMP_AUDIOS_DIR)
        output_path = extract_audio(request.video_path, output_dir)
        return {
            "message": "Audio extracted successfully", 
            "output_path": output_path
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))