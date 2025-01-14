# concept_map_service.py

from pathlib import Path
import subprocess
from datetime import datetime
from src.text_to_concept_map.text_to_concept_map import (
    extract_concept_map_elements,
    generate_mermaid_code_from_elements,
    save_to_file,
    set_png_dpi
)
import os
from src.config import Config

def generate_concept_map_file(
    summary_text: str = None,
    summary_file: str = None,
    output_dir: str = None
) -> str:
    """
    Generates a concept map PNG from either:
      - a raw summary text (summary_text), or
      - a summary file (summary_file).
    """
    output_dir = output_dir or str(Config.CONCEPT_MAP_OUTPUT_DIR)
    output_dir_obj = Path(output_dir)
    output_dir_obj.mkdir(parents=True, exist_ok=True)

    # Build a unique base name with a timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    if summary_file:
        summary_stem = Path(summary_file).stem.replace("summary_", "")
    else:
        summary_stem = "in_memory_summary"

    base_name = f"{summary_stem}_{timestamp}"
    output_png_path = output_dir_obj / f"concept_map_{base_name}.png"

    try:
        # Extract concept map elements from summary_text
        elements = extract_concept_map_elements(summary_text)
        # Convert them to Mermaid code
        mermaid_code = generate_mermaid_code_from_elements(elements)
        # Write Mermaid code to a temporary .mmd file
        temp_mmd_path = output_dir_obj / f"temp_{base_name}.mmd"
        save_to_file(mermaid_code, temp_mmd_path)

        command_png = [
            Config.MERMAID_CLI_PATH,
            "-i", str(temp_mmd_path),
            "-o", str(output_png_path),
            "-s", "4",
            "-t", "default",
            "-b", "transparent",
            "--no-sandbox"
        ]
        subprocess.run(command_png, check=True)

        temp_mmd_path.unlink()
        set_png_dpi(output_png_path, 300)

        return str(output_png_path.resolve())

    except Exception as e:
        raise Exception(f"Concept map generation failed: {str(e)}")
