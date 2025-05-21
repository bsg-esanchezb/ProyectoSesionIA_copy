from src.transcription.transcribe_audio import transcribe_audio # Corrected import
from pathlib import Path
import os
from src.config import Config

def transcribe_audio_file(
    audio_file_url: str, # Renamed from audio_file_path; must be a URL
    output_directory: str = None
) -> tuple[str, str]:
    """
    Transcribes an audio file (accessible via URL) to text using Azure Speech-to-Text.
    Saves the extracted text to a .txt file and the raw Azure JSON response to a .json file.
    
    Args:
        audio_file_url (str): Publicly accessible URL to the input audio file.
        output_directory (str, optional): Directory where the transcription text file 
                                         and raw Azure JSON response file will be saved.
                                         Defaults to Config.TRANSCRIPTIONS_OUTPUT_DIR.
    
    Returns:
        tuple[str, str]: A tuple containing (transcription_text, path_to_saved_transcription_text_file).
    
    Raises:
        Exception: If the transcription process fails.
    """
    # Use paths from Config if not provided
    output_directory = output_directory or Config.TRANSCRIPTIONS_OUTPUT_DIR

    try:
        # Ensure output directory exists
        os.makedirs(output_directory, exist_ok=True)
        # temp_chunks_directory logic is removed

        # Derive a file stem for naming output files.
        # This attempts to get the last part of the URL and use its stem.
        # Example: "http://example.com/audio/my_lecture.mp3" -> "my_lecture"
        # This might need to be made more robust if URLs are not predictable.
        try:
            url_filename = Path(audio_file_url.split('?')[0].split('/')[-1]) # Get last part, ignore query params
            file_stem = url_filename.stem if url_filename.stem else "transcription_output"
        except Exception:
            file_stem = "transcription_output" # Fallback stem

        # Define path for the raw Azure JSON response (saved by transcribe_audio)
        raw_json_filename = f"{file_stem}_azure_raw_response.json"
        raw_json_output_path = Path(output_directory) / raw_json_filename

        # Define path for the final extracted transcription text (saved by this service)
        extracted_text_filename = f"{file_stem}_transcription.txt"
        final_text_output_path = Path(output_directory) / extracted_text_filename
        
        # Call the modified transcribe_audio function from src.transcription.transcribe_audio
        # It now takes audio_file_url and output_transcription_file_path (for the raw JSON)
        # It returns the extracted text.
        transcription_text = transcribe_audio(
            audio_file_url=audio_file_url, # Pass the URL
            output_transcription_file_path=str(raw_json_output_path) # Path to save raw JSON
        )
        
        # Save the extracted transcription_text to its own file
        with open(final_text_output_path, "w", encoding="utf-8") as file:
            file.write(transcription_text)
            
        return transcription_text, str(final_text_output_path) # Return extracted text and its path
    
    except Exception as e:
        # Consider more specific error logging or re-raising with more context
        raise Exception(f"Transcription service failed for URL '{audio_file_url}': {str(e)}")
