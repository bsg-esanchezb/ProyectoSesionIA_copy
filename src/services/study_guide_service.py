# study_guide_service.py

from pathlib import Path
from datetime import datetime
from text_to_pdf.text_to_pdf import StudyGuideGenerator
from config import Config

def generate_study_guide_pdf(
    summary_text: str = None,
    summary_file: str = None,
    output_dir: str = None
) -> str:
    """
    Generates a PDF from a summary, using a timestamp in the filename 
    to avoid overwriting older documents.
    """
    # fallback to config path
    output_dir = output_dir or str(Config.STUDY_GUIDE_OUTPUT_DIR)

    # build a unique base name with a timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    # optionally incorporate the summary_file's stem
    base_name = "in_memory_summary"
    if summary_file:
        base_name = Path(summary_file).stem

    base_name = f"{base_name}_{timestamp}"

    output_path = Path(output_dir) / f"{base_name}_study_guide.pdf"

    try:
        generator = StudyGuideGenerator()
        generator.create_study_guide_from_text(summary_text, str(output_path))
        return str(output_path)
    except Exception as e:
        raise Exception(f"Error generating study guide PDF: {str(e)}")
