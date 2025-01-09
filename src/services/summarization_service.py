from pathlib import Path
from src.summarization.summarization import Summarizer
from src.config import Config

def summarize_transcription(transcription_file: str, output_dir: str = None) -> tuple[str, str]:
    """
    Summarizes a transcription file using OpenAI's Whisper model and saves the result.
    
    Args:
        transcription_file (str): Path to the input transcription file.
        output_dir (str, optional): Directory where the summary file will be saved.
                                    If not provided, the value from the config will be used.
    
    Returns:
        tuple[str, str]: A tuple containing (summary_text, output_file_path)

    Raises:
        Exception: If summarization fails or the transcription file is invalid.
    """
    # Use the path from Config if no output directory is provided
    output_dir = output_dir or Config.TEMP_SUMMARY_DIR

    transcription_path = Path(transcription_file)
    if not transcription_path.exists() or not transcription_path.is_file():
        raise Exception("Transcription file not found or is not a valid file.")

    # Generate the output filename using the transcription file name
    output_file_name = f"{transcription_path.stem}_summary.txt"
    output_path = Path(output_dir) / output_file_name

    summarizer = Summarizer()

    # Generate the summary and return the text along with the file path
    summary_text = summarizer.analyze_transcription(
        transcription_file=str(transcription_path),
        output_file=str(output_path)
    )

    return summary_text, str(output_path)
