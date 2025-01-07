import subprocess
from fastapi import APIRouter, HTTPException
from pathlib import Path
from pydantic import BaseModel
from services.concept_map_service import generate_concept_map_file

router = APIRouter()

# Default paths
DEFAULT_SUMMARY_PATH = r"C:\Users\esanchezb\Documents\Project_cafe_v2\data\temp\summary\summary.txt"
DEFAULT_OUTPUT_DIR = r"C:\Users\esanchezb\Documents\Project_cafe_v2\data\output\concept_map"

class ConceptMapRequest(BaseModel):
    summary_path: str = DEFAULT_SUMMARY_PATH
    output_dir: str = DEFAULT_OUTPUT_DIR

@router.post("/generate-concept-map", summary="Generate Concept Map", tags=["ConceptMap"])
def generate_concept_map_endpoint(request: ConceptMapRequest):
    try:
        summary_path = Path(request.summary_path)
        output_dir = Path(request.output_dir)

        if not summary_path.exists():
            raise HTTPException(status_code=400, detail="Summary file does not exist.")

        png_path = generate_concept_map_file(str(summary_path), str(output_dir))
        return {
            "message": "Concept map generated successfully",
            "output_path": png_path
        }

    except subprocess.CalledProcessError as cpe:
        raise HTTPException(status_code=500, detail=f"Mermaid CLI failed: {cpe}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
