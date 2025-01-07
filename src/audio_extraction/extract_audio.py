from moviepy.editor import VideoFileClip
from pathlib import Path
import os

class AudioExtractionError(Exception):
    """Custom exception for audio extraction errors"""
    pass

def validate_paths(video_path: str, output_path: str) -> tuple[Path, Path]:
    """
    Validates input and output paths.
    
    Args:
        video_path (str): Path to input video file
        output_path (str): Path for output audio file
    
    Returns:
        tuple[Path, Path]: Validated video and audio paths
    
    Raises:
        AudioExtractionError: If paths are invalid
    """
    video_path = Path(video_path)
    output_path = Path(output_path)
    
    if not video_path.exists():
        raise AudioExtractionError(f"Video file not found: {video_path}")
    
    if not video_path.is_file():
        raise AudioExtractionError(f"Video path is not a file: {video_path}")
        
    # Create output directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    return video_path, output_path

def extract_audio_from_video(video_path: str, audio_output_path: str = None) -> str:
    """
    Extracts audio from video with hardcoded MP3 format and 192k bitrate.
    
    Args:
        video_path (str): Path to input video file
        audio_output_path (str, optional): Path for output audio file
        
    Returns:
        str: Path to the extracted audio file
        
    Raises:
        AudioExtractionError: If extraction fails
    """
    try:
        # Default output path if not provided
        if audio_output_path is None:
            video_path_obj = Path(video_path)
            audio_output_path = str(video_path_obj.parent / f"{video_path_obj.stem}.mp3")

        video_path, audio_output_path = validate_paths(video_path, audio_output_path)
        video = VideoFileClip(str(video_path))

        if video.audio is None:
            video.close()
            raise AudioExtractionError("No audio stream found in video file")

        print(f"Extracting audio to: {audio_output_path}")
        video.audio.write_audiofile(str(audio_output_path), bitrate="192k", codec="libmp3lame")
        video.close()
        return str(audio_output_path)
    
    except Exception as e:
        raise AudioExtractionError(f"Failed to extract audio: {str(e)}")

def main():
    """
    Main execution function for single video extraction
    """
    # Define paths
    INPUT_VIDEO_PATH = r"C:\Users\esanchezb\Documents\Project_cafe_v2\data\input\videos\OCTUBRE_18_10_24_CERTI_R_DATA_SCIENTIST_ONLINE_2024_I_LIMA_Curso_CRISP_DM_en_Proyectos_de_Data_Science_ONLINE_2024_I_17_10_24.mp4"
    OUTPUT_DIR = r"C:\Users\esanchezb\Documents\Project_cafe_v2\data\temp\audios"
    
    # Generate the output path in the specified directory
    video_path_obj = Path(INPUT_VIDEO_PATH)
    OUTPUT_AUDIO_PATH = str(Path(OUTPUT_DIR) / f"{video_path_obj.stem}.mp3")

    # Single video extraction with hardcoded settings
    print("\n=== Single Video Extraction ===")
    try:
        output_path = extract_audio_from_video(INPUT_VIDEO_PATH, OUTPUT_AUDIO_PATH)
        print(f"Successfully extracted audio to: {output_path}")
    except AudioExtractionError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
    