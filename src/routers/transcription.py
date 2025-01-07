from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
from services.transcription_service import transcribe_audio_file
from config import Config  # Import the Config class

router = APIRouter()

class TranscriptionRequest(BaseModel):
    audio_file_path: str
    output_directory: str = None
    temp_chunks_directory: str = None

@router.post("/transcribe", summary="Transcribe audio to text", tags=["Transcription"])
async def transcribe_audio_endpoint(request: TranscriptionRequest):
    """
    Transcribes MP3 audio to text using OpenAI's Whisper API.
    The result is saved with '_transcription' appended to the original filename.
    """
    try:
        # Validate input file
        audio_file_path = Path(request.audio_file_path)
        if not audio_file_path.exists() or not audio_file_path.is_file():
            raise HTTPException(status_code=400, detail="Audio file not found.")
        
        # Use provided directories or fallback to Config
        output_directory = request.output_directory or str(Config.TRANSCRIPTIONS_OUTPUT_DIR)
        temp_chunks_directory = request.temp_chunks_directory or str(Config.TEMP_CHUNKS_DIR)

        # Use the service function with the paths
        transcription_text, final_path = transcribe_audio_file(
            audio_file_path=str(audio_file_path),
            output_directory=output_directory,
            temp_chunks_directory=temp_chunks_directory
        )

        return {
            "message": "Transcription completed successfully",
            "transcription_text": transcription_text,
            "output_path": final_path
        }
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
