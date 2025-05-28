from src.transcription.transcribe_audio import transcribe_audio_azure
from src.services.blob_service import upload_file_to_blob
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
        print("antes de verificar la creacion de los directorios")
        os.makedirs(output_directory, exist_ok=True)
        os.makedirs(temp_chunks_directory, exist_ok=True)
        print("antes de declarar las direcciones del audio path")
        audio_path = Path(audio_file_path)
        print("antes de declarar las direcciones del output path")
        output_path = Path(output_directory) / f"{audio_path.stem}_transcription.txt"

        # Upload audio to Azure Blob Storage
        print(f"Uploading {audio_path} to Azure Blob Storage in subfolder {Config.AZURE_BLOB_SUBFOLDER_TEMP_AUDIO}...")
        audio_url = upload_file_to_blob(
            local_path=str(audio_path),
            blob_subfolder=Config.AZURE_BLOB_SUBFOLDER_TEMP_AUDIO
        )
        print(f"Audio uploaded to: {audio_url}")

        # Call Azure transcription service
        transcription_text = transcribe_audio_azure(
            audio_url=audio_url,
            output_transcription_path=str(output_path)
            # locale can be passed if needed, default is "es-ES" in transcribe_audio_azure
        )
        
        return transcription_text, str(output_path)
    except Exception as e:
        # Consider more specific error logging here if needed
        raise Exception(f"Transcription failed: {str(e)}")
