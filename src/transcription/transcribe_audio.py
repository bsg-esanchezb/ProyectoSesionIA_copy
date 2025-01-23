import openai
from pydub import AudioSegment
from pydub.utils import make_chunks
from tqdm import tqdm
import os
import glob
from pathlib import Path
from dotenv import load_dotenv
from shutil import which

# Load environment variables
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Dynamically detect ffmpeg and ffprobe paths with a fallback to .env
def set_ffmpeg_paths():
    ffmpeg_path = os.getenv('FFMPEG_PATH') or which("ffmpeg")
    ffprobe_path = os.getenv('FFPROBE_PATH') or which("ffprobe")

    if not ffmpeg_path or not ffprobe_path:
        raise FileNotFoundError("ffmpeg or ffprobe not found. Ensure they are installed and correctly set.")
    
    AudioSegment.ffmpeg = ffmpeg_path
    AudioSegment.ffprobe = ffprobe_path
    print(f"[DEBUG] ffmpeg path set to: {ffmpeg_path}")
    print(f"[DEBUG] ffprobe path set to: {ffprobe_path}")

# Call once to set paths globally
set_ffmpeg_paths()

def cleanup_temp_files(temp_chunks_path):
    """Clean up temporary WAV chunks"""
    temp_files = glob.glob(os.path.join(temp_chunks_path, "temp_chunk_*.wav"))
    for temp_file in temp_files:
        try:
            os.remove(temp_file)
        except Exception as e:
            print(f"Warning: Could not remove temporary file {temp_file}: {str(e)}")

def get_file_size(file_path):
    """Get file size in bytes"""
    return os.path.getsize(file_path)

def validate_mp3_file(file_path):
    """Validate if file is MP3 and exists"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")
    
    if not file_path.lower().endswith('.mp3'):
        raise ValueError(f"File must be MP3 format: {file_path}")

def transcribe_audio(audio_file_path, output_transcription_path, temp_chunks_path) -> str:
    """
    Transcribe MP3 audio file to text using OpenAI's Whisper model
    
    Args:
        audio_file_path (str): Path to input MP3 file
        output_transcription_path (str): Path where to save transcription
        temp_chunks_path (str): Directory for temporary chunk files
    
    Returns:
        str: The complete transcription text
    """
    print(f"[DEBUG] Using ffmpeg path: {AudioSegment.ffmpeg}")
    print(f"[DEBUG] Using ffprobe path: {AudioSegment.ffprobe}")

    print("validando el archivo mp3")
    validate_mp3_file(audio_file_path)
    os.makedirs(temp_chunks_path, exist_ok=True)
    cleanup_temp_files(temp_chunks_path)
    full_transcription = ""

    try:
        print(f"Loading MP3 file: {audio_file_path}")
        # This will fail if ffmpeg/ffprobe are not found
        audio = AudioSegment.from_mp3(audio_file_path)
        
        chunk_length_ms = 60 * 1000
        chunks = make_chunks(audio, chunk_length_ms)
        total_chunks = len(chunks)

        print(f"Starting transcription of {total_chunks} chunks...")
        for i, chunk in enumerate(tqdm(chunks, desc="Processing chunks"), 1):
            chunk_path = os.path.join(temp_chunks_path, f"temp_chunk_{i}.wav")
            try:
                chunk.export(chunk_path, format="wav")
                
                file_size = get_file_size(chunk_path)
                if file_size > 25 * 1024 * 1024:
                    print(f"\nWarning: Chunk {i} is {file_size/1024/1024:.2f}MB, exceeding 25MB limit. Skipping...")
                    continue
                
                with open(chunk_path, "rb") as audio_file:
                    response = openai.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language="es"
                    )
                full_transcription += response.text + " "

            except Exception as e:
                print(f"\nError processing chunk {i}: {str(e)}")
            
            finally:
                if os.path.exists(chunk_path):
                    os.remove(chunk_path)

        print("\nTranscription completed!")
        
        os.makedirs(os.path.dirname(output_transcription_path), exist_ok=True)
        with open(output_transcription_path, "w", encoding="utf-8") as file:
            file.write(full_transcription.strip())
            
        return full_transcription.strip()

    except Exception as e:
        raise

    finally:
        cleanup_temp_files(temp_chunks_path)

def main():
    """Main execution function"""
    try:
        # Define the absolute paths directly
        input_mp3 = r"C:\Users\esanchezb\Documents\Project_cafe_v2\data\temp\audios\OCTUBRE_18_10_24_CERTI_R_DATA_SCIENTIST_ONLINE_2024_I_LIMA_Curso_CRISP_DM_en_Proyectos_de_Data_Science_ONLINE_2024_I_17_10_24.mp3"
        output_text = r"C:\Users\esanchezb\Documents\Project_cafe_v2\data\output\transcriptions\transcription.txt"
        temp_dir = r"C:\Users\esanchezb\Documents\Project_cafe_v2\data\temp\chunks"

        # Ensure required directories exist
        os.makedirs(temp_dir, exist_ok=True)
        os.makedirs(os.path.dirname(output_text), exist_ok=True)

        # Check if OpenAI API key is set
        if not openai.api_key:
            raise ValueError("OpenAI API key not found. Please check your .env file.")

        print(f"Processing MP3 file: {input_mp3}")
        print(f"Output will be saved to: {output_text}")
        print(f"Using temporary directory: {temp_dir}")

        # Start transcription
        transcribe_audio(input_mp3, output_text, temp_dir)

    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

    return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
