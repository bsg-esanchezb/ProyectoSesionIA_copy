from pathlib import Path
from datetime import datetime
from src.text_to_pdf.text_to_pdf import StudyGuideGenerator
from src.config import Config

def generate_study_guide_pdf(
    summary_text: str = None,
    summary_file: str = None,
    output_dir: str = None,
    pe_sesion_val: int = None
) -> str:
    """
    Generates a PDF from a summary, with a name:
      "{IdPEspecificoSesion}_{timestamp}_study_guide.pdf"
    If pe_sesion_val is None, fallback to something else.
    """
    output_dir = output_dir or str(Config.STUDY_GUIDE_OUTPUT_DIR)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    # Si pasaste summary_file, leemos su "stem". De lo contrario, usaremos "no_summaryfile"
    base_stem = "no_summaryfile"
    if summary_file:
        base_stem = Path(summary_file).stem

    # Si tenemos un pe_sesion_val:
    if pe_sesion_val:
        # nombre quedaría algo como: "9999_20250131_143012_123456_study_guide.pdf"
        # o si quieres incluir base_stem: "base_stem_9999_20250131_..."
        file_name = f"{pe_sesion_val}_{timestamp}_study_guide.pdf"
    else:
        file_name = f"{base_stem}_{timestamp}_study_guide.pdf"

    output_path = Path(output_dir) / file_name

    try:
        generator = StudyGuideGenerator()
        generator.create_study_guide_from_text(summary_text, str(output_path))
        return str(output_path)
    except Exception as e:
        raise Exception(f"Error generating study guide PDF: {str(e)}")