from src.transcription.transcribe_audio import transcribe_audio
from pathlib import Path
import os
from src.config import Config

def transcribe_audio_file(
    audio_file_path: str,
    output_directory: str = None,
    temp_chunks_directory: str = None
) -> tuple[str, str]:
    """
    Transcribes an MP3 audio file to text using OpenAI's Whisper model.
    
    Args:
        audio_file_path (str): Path to the input MP3 audio file.
        output_directory (str, optional): Directory where the transcription will be saved.
        temp_chunks_directory (str, optional): Directory for storing temporary audio chunks.
    
    Returns:
        tuple[str, str]: A tuple containing (transcription_text, output_file_path)
    
    Raises:
        Exception: If the transcription process fails.
    """
    # Use paths from Config if not provided
    output_directory = output_directory or Config.TRANSCRIPTIONS_OUTPUT_DIR
    temp_chunks_directory = temp_chunks_directory or Config.TEMP_CHUNKS_DIR

    try:
        os.makedirs(output_directory, exist_ok=True)
        os.makedirs(temp_chunks_directory, exist_ok=True)
        
        audio_path = Path(audio_file_path)
        output_path = Path(output_directory) / f"{audio_path.stem}_transcription.txt"
        
        transcription_text = transcribe_audio(
            audio_file_path=str(audio_path),
            output_transcription_path=str(output_path),
            temp_chunks_path=str(temp_chunks_directory)
        )
        
        return transcription_text, str(output_path)
    except Exception as e:
        raise Exception(f"Transcription failed: {str(e)}")
