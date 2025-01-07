from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.study_guide_service import generate_study_guide_pdf

router = APIRouter()

class StudyGuideRequest(BaseModel):
    summary_file: str
    output_dir: str = None  # Optionally provide an output directory

@router.post("/generate", summary="Generate Study Guide PDF", tags=["Study Guide"])
def generate_study_guide_endpoint(request: StudyGuideRequest):
    """
    Generate a PDF study guide from a summary file.
    If output_dir is provided, use it, otherwise use the default directory.
    """
    try:
        output_path = generate_study_guide_pdf(
            summary_file=request.summary_file,
            output_dir=request.output_dir
        )
        return {
            "message": "Study guide PDF generated successfully.",
            "output_path": output_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
