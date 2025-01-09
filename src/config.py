import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent.parent  # Project root directory
ENV_FILE = BASE_DIR / '.env'
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)

class Config:
    # Secrets / Tokens
    VIMEO_ACCESS_TOKEN = os.getenv("VIMEO_ACCESS_TOKEN", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")

    # Database and Celery
    DATABASE_URL = os.getenv("DATABASE_URL", "")
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "")

    # Base directories
    DATA_DIR = BASE_DIR / 'data'
    INPUT_VIDEO_DIR = DATA_DIR / 'input' / 'videos'
    OUTPUT_DIR = DATA_DIR / 'output'
    TEMP_DIR = DATA_DIR / 'temp'

    # Output subdirectories
    CONCEPT_MAP_OUTPUT_DIR = OUTPUT_DIR / 'concept_map'
    PODCAST_OUTPUT_DIR = OUTPUT_DIR / 'podcast'
    STUDY_GUIDE_OUTPUT_DIR = OUTPUT_DIR / 'study_guides'
    TRANSCRIPTIONS_OUTPUT_DIR = OUTPUT_DIR / 'transcriptions'
    VIDEOS_OUTPUT_DIR = OUTPUT_DIR / 'videos'

    # Temporary subdirectories
    TEMP_SUMMARY_DIR = TEMP_DIR / 'summary'
    TEMP_PODCAST_DIR = TEMP_DIR / 'podcast'
    TEMP_AUDIOS_DIR = TEMP_DIR / 'audios'
    TEMP_CHUNKS_DIR = TEMP_DIR / 'chunks'

    # Mermaid CLI location
    MERMAID_CLI_PATH = os.getenv("MERMAID_CLI_PATH", r"C:\Users\esanchezb\AppData\Roaming\npm\mmdc.cmd")
