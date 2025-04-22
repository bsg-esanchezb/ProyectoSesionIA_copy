from pathlib import Path
from datetime import datetime
from src.text_to_audio.text_to_audio import (
    generate_podcast_script,
    text_to_speech_google
)
import os
from src.config import Config

from pathlib import Path
from datetime import datetime
from src.text_to_audio.text_to_audio import (
    generate_podcast_script,
    text_to_speech_google
)
import os
from src.config import Config

def generate_podcast(
    summary_text: str = None,
    summary_file: str = None,
    audio_output: str = None,
    script_output: str = None,
    pe_sesion_val: int = None,
    db = None,
    sesion_id: int = None
) -> dict:
    """
    Generates a podcast from either raw summary text or a summary file.
    Appends a timestamp and, if available, the IdPEspecificoSesion to filenames to avoid collisions.
    """
    # Set default output paths if not provided
    audio_output = audio_output or str(Config.PODCAST_OUTPUT_DIR / "podcast_summary.wav")
    script_output = script_output or str(Config.TEMP_PODCAST_DIR / "podcast_script.txt")
    
    # Build a unique base name with a timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    if pe_sesion_val:
        base_stem = f"{pe_sesion_val}_{timestamp}"
    else:
        base_stem = f"podcast_{timestamp}"

    # Use base_stem to create filenames
    script_output_path = Path(script_output).parent / f"{base_stem}_script.txt"
    audio_output_path = Path(audio_output).parent / f"{base_stem}_podcast.wav"

    try:
        # Generate the podcast script from the summary text
        podcast_script = generate_podcast_script(summary_text)

        # Write the script to disk
        script_output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(script_output_path, "w", encoding="utf-8") as script_file:
            script_file.write(podcast_script)
        
        if db and pe_sesion_val:
            from src.repositories.procesamiento_repository import update_texto_guion_audio
            update_texto_guion_audio(db=db, sesion_id=sesion_id, texto_guion_audio=podcast_script)

        # Convert the script to audio
        audio_output_path.parent.mkdir(parents=True, exist_ok=True)
        text_to_speech_google(podcast_script, audio_output_path)

        return {
            "script_output": str(script_output_path),
            "audio_output": str(audio_output_path)
        }
    except Exception as e:
        raise Exception(f"Podcast generation failed: {str(e)}")
