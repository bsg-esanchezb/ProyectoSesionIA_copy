from pathlib import Path
from openai import OpenAI
from google.cloud import texttospeech
from dotenv import load_dotenv
from pydub import AudioSegment
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
openai_client = OpenAI(api_key=openai_api_key)
google_credentials_path = r'C:\Users\esanchezb\Documents\Project_cafe_v2\text_to_speech_credential.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = google_credentials_path

# Define constants
GOOGLE_VOICE = 'es-US-Polyglot-1'
MAX_CHARACTERS = 4096  # Character limit per request
DEFAULT_GPT_TEMPERATURE = 0.4  # Default temperature for GPT model

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
        combined.export(str(output_file), format="wav")

    except Exception as e:
        raise RuntimeError(f"Failed to concatenate audio files: {str(e)}")

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
Eres un narrador experto especializado en crear contenido educativo que sea fácil de seguir mientras se conduce. Tu objetivo es transformar el resumen de clase proporcionado en una narración cautivadora en español, diseñada específicamente para ser escuchada durante trayectos en coche.

ESTILO DE NARRACIÓN:
- Usa un tono conversacional y amigable, como si estuvieras hablando con un amigo inteligente
- Evita palabras rebuscadas o estructuras complejas
- Mantén las oraciones cortas y fáciles de seguir
- No uses marcadores formales como "introducción", "en conclusión" o "en primer lugar"
- Conecta las ideas de forma natural, como en una conversación fluida

ESTRUCTURA:
- Comienza con un gancho interesante o una pregunta provocadora relacionada con el tema
- Presenta las ideas principales de forma gradual y conectada
- Usa analogías y ejemplos de la vida cotidiana para explicar conceptos complejos
- Incluye micro-pausas naturales entre ideas importantes
- Mantén cada segmento entre 2-3 minutos para facilitar la atención

CARACTERÍSTICAS CLAVE:
- Frases cortas y directas que sean fáciles de procesar mientras se conduce
- Repetición estratégica de puntos clave de forma natural
- Transiciones suaves y conversacionales entre ideas
- Ritmo pausado que permita la absorción de información
- Énfasis en las aplicaciones prácticas y relevantes del contenido

EVITAR:
- Jerga técnica innecesaria
- Estructuras gramaticales complejas
- Referencias a elementos visuales o que requieran atención visual
- Listas largas o enumeraciones extensas
- Datos específicos difíciles de recordar

El contenido a transformar es el siguiente:
{}

Recuerda: La persona que escucha está conduciendo. Necesita poder seguir el hilo sin esfuerzo y sin perder la concentración en la carretera.
"""
    try:
        summary_parts = split_text(summary)
        full_script = ""

        for part in summary_parts:
            prompt = prompt_template.format(part)
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Eres un experto en temas STEM"},
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