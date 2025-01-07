from audio_extraction.extract_audio import extract_audio_from_video, AudioExtractionError
import os
from config import Config

def extract_audio(video_path: str, output_directory: str = None) -> str:
    """
    Extracts audio from a given video using the underlying extraction logic.

    Args:
        video_path (str): Path to the video file.
        output_directory (str, optional): Directory to save the extracted audio. 
                                          Defaults to the configured path in Config.

    Returns:
        str: The path to the extracted audio file.

    Raises:
        Exception: If audio extraction fails.
    """
    # Use the existing TEMP_AUDIOS_DIR from Config
    output_directory = output_directory or str(Config.TEMP_AUDIOS_DIR)

    try:
        # Ensure the output directory exists
        os.makedirs(output_directory, exist_ok=True)
        
        # Generate output filename based on the video filename
        video_filename = os.path.basename(video_path)
        audio_filename = f"{os.path.splitext(video_filename)[0]}.mp3"
        audio_output_path = os.path.join(output_directory, audio_filename)
        
        # Perform the audio extraction using the helper function
        output_path = extract_audio_from_video(video_path, audio_output_path)
        return output_path
    except AudioExtractionError as e:
        raise Exception(f"Audio extraction failed: {str(e)}")

