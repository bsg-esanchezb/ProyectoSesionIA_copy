from pathlib import Path
from openai import OpenAI
from google.cloud import texttospeech
from pydub import AudioSegment
import os
import logging
from src.config import Config  # Importing the config class
import gc

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load OpenAI API key from Config
openai_api_key = Config.OPENAI_API_KEY
openai_client = OpenAI(api_key=openai_api_key)

# Set Google Cloud Credentials from Config
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = Config.GOOGLE_APPLICATION_CREDENTIALS

# Define constants
GOOGLE_VOICE = 'es-US-Polyglot-1'
MAX_CHARACTERS = 4096  # Character limit per request
DEFAULT_GPT_TEMPERATURE = 0.5  # Default temperature for GPT model

def split_text(text, max_length=MAX_CHARACTERS):
    """Split text into chunks of max_length characters."""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        word_length = len(word) + 1  # +1 for space
        if current_length + word_length > max_length:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = word_length
        else:
            current_chunk.append(word)
            current_length += word_length

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks

def text_to_speech_google(script_text, output_file, audio_format="wav"):
    """Generate TTS audio using Google's Polyglot voice in WAV format."""
    try:
        google_client = texttospeech.TextToSpeechClient()
        script_parts = split_text(script_text)
        temp_files = []

        logger.info(f"Processing {len(script_parts)} parts for {GOOGLE_VOICE}")

        for i, part in enumerate(script_parts):
            try:
                synthesis_input = texttospeech.SynthesisInput(text=part)
                voice = texttospeech.VoiceSelectionParams(
                    language_code='es-US',
                    name=GOOGLE_VOICE
                )
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.LINEAR16
                )
                response = google_client.synthesize_speech(
                    input=synthesis_input,
                    voice=voice,
                    audio_config=audio_config
                )
                temp_output = str(output_file.parent / f"{output_file.stem}_part_{i + 1}.{audio_format.lower()}")
                temp_files.append(temp_output)
                with open(temp_output, 'wb') as out:
                    out.write(response.audio_content)

            except Exception as e:
                raise RuntimeError(f"Error processing part {i + 1}: {str(e)}")
            
            finally:
                del response
                gc.collect()

        if temp_files:
            concatenate_audio_files(temp_files, output_file)

            # Clean up temporary files
            for temp_file in temp_files:
                try:
                    os.remove(temp_file)
                except Exception as e:
                    logger.warning(f"Could not remove temp file {temp_file}: {str(e)}")

        return output_file

    except Exception as e:
        raise RuntimeError(f"Failed to generate audio: {str(e)}")

def concatenate_audio_files(input_files, output_file):
    """Concatenate multiple audio files into a single output file."""
    try:
        combined = AudioSegment.empty()
        for file in input_files:
            audio = AudioSegment.from_file(file)
            combined += audio
            del audio
        combined.export(str(output_file), format="wav")

    except Exception as e:
        raise RuntimeError(f"Failed to concatenate audio files: {str(e)}")
    
    finally:
        del combined
        gc.collect()

def generate_podcast_script(summary, temperature=DEFAULT_GPT_TEMPERATURE):
    """
    Generate a narrated audio script in Spanish using OpenAI's GPT model.
    
    Args:
        summary (str): The text summary to convert into a podcast script
        temperature (float): Controls randomness in the output. Higher values (e.g., 0.8) make the output more random,
                           while lower values (e.g., 0.2) make it more focused and deterministic.
                           Defaults to DEFAULT_GPT_TEMPERATURE (0.7)
    """
    logger.info(f"Generating podcast script with temperature: {temperature}")
    
    prompt_template = """
Paraphrase the given document in a professional narrative tone, beginning with a short, friendly welcome phrase, and developing the topics as if presenting an informative exposition. Make sure to preserve all essential aspects and details without omitting any critical information. Avoid using phrases like "We have seen" or "We have developed" in order to maintain a narrative suitable for an audiobook.
Steps
Read the original document: Make sure to fully understand the content of the document before attempting to paraphrase it.


Identify key ideas and topics: Look for the main ideas and critical details, and develop the themes as though you are giving a presentation.


Rewrite the content: Use a professional narrative style to rephrase the document, paying attention to the flow and clarity of the narrative. Avoid expressions such as "We have seen" or "We have developed."


Review and compare: Compare the new narrative with the original document to ensure that all information is present and no data has been omitted.


Output Format
The output should be a professional narrative with a welcoming phrase like "Welcome! In this study guide..." or "Welcome! Next, we will...", of an appropriate length for an audiobook, maintaining all the original content while developing the topics in an expository manner.
Examples
Input:
 "The report mentions that climate change is affecting crops in various regions, leading to significant economic losses."
Output:
 "Welcome! In this study guide, we will explore the impact of climate change on crop production across different regions. We will examine the challenges faced by agricultural producers and how climate variability is influencing both production and food security globally, resulting in substantial economic losses that highlight the far-reaching consequences of this phenomenon on the agricultural economy."
Notes
Ensure the tone is professional and fluid, suitable for audiobook narration.
Do not omit information or alter the original meaning of the text.
Output language speech must be written in spanish latin american.
this is the content to narrate: {}
"""
    try:
        summary_parts = split_text(summary)
        full_script = ""

        for part in summary_parts:
            prompt = prompt_template.format(part)
            response = openai_client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": "You are an expert in educational narrations and STEM topics"},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature
            )
            full_script += response.choices[0].message.content

        return full_script

    except Exception as e:
        raise RuntimeError(f"Failed to generate podcast script: {str(e)}")

def generate_podcast_from_text(summary_text: str,
                             audio_output: str,
                             script_output: str = None,
                             temperature: float = DEFAULT_GPT_TEMPERATURE) -> dict:
    """
    Generates a podcast from raw summary text (rather than reading a summary file).
    
    Args:
        summary_text (str): The raw summary text to convert into a podcast.
        audio_output (str): Path to the final audio file (e.g., .wav).
        script_output (str): Where to save the generated script (optional).
        temperature (float): Controls GPT's output randomness. Higher values (0.8+) increase creativity,
                           lower values (0.2-0.5) increase focus and determinism.
                           Defaults to DEFAULT_GPT_TEMPERATURE (0.7).

    Returns:
        dict: A dictionary containing 'script_output' and 'audio_output' paths.
    """
    try:
        logger.info(f"Starting podcast generation with temperature: {temperature}")
        
        # 1) Generate the podcast script using OpenAI
        podcast_script = generate_podcast_script(summary_text, temperature)

        # 2) If script_output is provided, save it
        if script_output:
            script_output_path = Path(script_output)
            script_output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(script_output_path, "w", encoding="utf-8") as script_file:
                script_file.write(podcast_script)
        else:
            script_output_path = None

        # 3) Generate the audio
        audio_output_path = Path(audio_output)
        audio_output_path.parent.mkdir(parents=True, exist_ok=True)
        text_to_speech_google(podcast_script, audio_output_path)

        return {
            "script_output": str(script_output_path) if script_output_path else None,
            "audio_output": str(audio_output_path)
        }
    except Exception as e:
        raise RuntimeError(f"Failed to generate podcast from text: {str(e)}")