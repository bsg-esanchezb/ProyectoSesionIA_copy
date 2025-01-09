from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.services.podcast_service import generate_podcast
from pathlib import Path

router = APIRouter()

# Default directories
DEFAULT_SUMMARY_PATH = r"C:\Users\esanchezb\Documents\Project_cafe_v2\data\temp\summary\transcription_summary.txt"
DEFAULT_AUDIO_OUTPUT_PATH = r"C:\Users\esanchezb\Documents\Project_cafe_v2\data\output\podcast\podcast_summary.wav"
DEFAULT_SCRIPT_OUTPUT_PATH = r"C:\Users\esanchezb\Documents\Project_cafe_v2\data\temp\podcast\podcast_script.txt"

class PodcastRequest(BaseModel):
    summary_file: str = DEFAULT_SUMMARY_PATH
    audio_output: str = DEFAULT_AUDIO_OUTPUT_PATH
    script_output: str = DEFAULT_SCRIPT_OUTPUT_PATH

@router.post("/generate-podcast", summary="Generate Podcast from Summary", tags=["Podcast"])
def generate_podcast_endpoint(request: PodcastRequest):
    try:
        result = generate_podcast(
            summary_file=request.summary_file,
            audio_output=request.audio_output,
            script_output=request.script_output
        )
        return {
            "message": "Podcast generated successfully",
            "script_output": result["script_output"],
            "audio_output": result["audio_output"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
