from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.services.summarization_service import summarize_transcription as summarize_transcription_service

router = APIRouter()

class SummaryRequest(BaseModel):
    transcription_file: str
    output_dir: str = None  # Make output directory optional

@router.post("/summarize", summary="Generate summary from transcription", tags=["Summary"])
async def summarize_transcription_endpoint(request: SummaryRequest):
    """
    Endpoint to generate a summary from a transcription file.
    If output_dir is provided, the summary is saved there; otherwise uses default.
    """
    try:
        output_path = summarize_transcription_service(
            transcription_file=request.transcription_file,
            output_dir=request.output_dir
        )
        return {
            "message": "Summary generated successfully",
            "output_path": output_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
