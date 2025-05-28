import os
import requests
import time
import uuid
import json
from pathlib import Path
from dotenv import load_dotenv

from src.config import Config

# Load environment variables if .env file exists
# Though Config class now handles .env loading for its attributes,
# this can remain if other parts of the script might use it directly.
BASE_DIR = Path(__file__).resolve().parent.parent.parent # Project root directory
ENV_FILE = BASE_DIR / '.env'
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)

# --- Azure Transcription Helper Functions ---

def _create_azure_transcription_job(audio_url: str, locale: str = "es-ES") -> str:
    """
    Creates an Azure batch transcription job.
    """
    print(f"Creating Azure transcription job for: {audio_url}")
    job_id = str(uuid.uuid4())
    transcription_url = f"https://{Config.AZURE_SPEECH_ENDPOINT}/speechtotext/transcriptions:submit?api-version=2024-11-15" # Using the specified API version

    headers = {
        "Ocp-Apim-Subscription-Key": Config.AZURE_SPEECH_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "contentUrls": [audio_url],
        "displayName": f"Transcription Job - {job_id}",
        "description": "Batch transcription job created via Python script",
        "locale": locale,
        "properties": {
            "wordLevelTimestampsEnabled": False, # Assuming word-level timestamps are not needed for now
            "timeToLive": "PT12H"  # Job will be available for 12 hours
        }
    }

    try:
        response = requests.post(transcription_url, headers=headers, json=payload)
        response.raise_for_status()  # Raises HTTPError for bad responses (4XX or 5XX)

        if response.status_code == 201: # Created
            status_url = response.headers.get("Location")
            if not status_url:
                raise Exception("Azure API did not return a Location header for the transcription status.")
            print(f"Successfully submitted transcription job. Status URL: {status_url}")
            return status_url
        else:
            # This case should ideally be caught by raise_for_status, but as a fallback:
            raise Exception(f"Failed to create transcription job. Status: {response.status_code}, Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error creating Azure transcription job: {e}")
        raise


def _get_azure_transcription_status(status_url: str) -> dict:
    """
    Gets the status of an Azure transcription job.
    """
    headers = {
        "Ocp-Apim-Subscription-Key": Config.AZURE_SPEECH_KEY
    }
    try:
        response = requests.get(status_url, headers=headers)
        response.raise_for_status()
        status_data = response.json()
        print(f"Transcription status: {status_data.get('status')}")
        return status_data
    except requests.exceptions.RequestException as e:
        print(f"Error getting transcription status from {status_url}: {e}")
        raise

def _wait_for_azure_transcription(status_url: str, poll_interval: int = 30) -> dict:
    """
    Polls Azure for transcription completion.
    """
    print(f"Waiting for transcription to complete. Polling status URL: {status_url}")
    while True:
        status_payload = _get_azure_transcription_status(status_url)
        job_status = status_payload.get("status")

        if job_status == "Succeeded":
            print("Transcription job succeeded.")
            return status_payload
        elif job_status == "Failed":
            error_info = status_payload.get("error", {})
            print(f"Transcription job failed. Error: {error_info.get('message', 'Unknown error')}")
            raise Exception(f"Azure transcription failed: {error_info.get('message', 'Unknown error')}")
        elif job_status in ["NotStarted", "Running"]:
            print(f"Job status is {job_status}. Waiting for {poll_interval} seconds...")
            time.sleep(poll_interval)
        else:
            print(f"Unknown job status: {job_status}. Payload: {status_payload}")
            raise Exception(f"Unknown Azure transcription status: {job_status}")

def _get_transcription_files_url_from_manifest(manifest_url: str) -> str:
    """
    Fetches the transcription manifest and extracts the content URL for the transcription result.
    """
    print(f"Fetching transcription manifest from: {manifest_url}")
    try:
        # Azure Storage URLs for results might not require a subscription key if they are SAS URLs
        # or if the service generates them to be publicly accessible for a short time.
        # If auth is needed, headers would be required here.
        response = requests.get(manifest_url)
        response.raise_for_status()
        manifest_data = response.json()

        for item in manifest_data.get("items", []):
            if item.get("kind") == "transcription":
                # The prompt specified "contentUrl", but Azure Batch v3.1 uses "contentUrl" within "results"
                # and the main manifest has "files" which then contains "contentUrl"
                # Let's assume manifest_url is the one from status_payload.get("links", {}).get("files")
                # This means manifest_data is the content of that "files" link.
                # The structure is usually:
                # { "values": [ { "name": "...", "kind": "transcription", "links": { "contentUrl": "..." } } ] }
                # OR based on recent Azure examples for batch:
                # The manifest_url directly points to a JSON listing files, one of which is the transcript.
                # The prompt implies manifest_url is the "files" link.
                # The actual transcription content URL is often nested.
                # The prompt says: "Parses the JSON manifest to find the item with "kind": "transcription". Returns the contentUrl"
                # Let's adjust based on a common structure for the "files" link payload.
                # It usually contains a list of result files.
                # Example: { "values": [ {"name": "xxx.json", "kind": "Transcription", "links": {"contentUrl": "URL_TO_TRANSCRIPT_JSON"}} ]}

                # The prompt seems to imply the manifest_url itself IS the JSON that lists various files.
                # And each item in that list has a "kind" and a "contentUrl".
                # Let's check the structure of manifest_data.
                # If manifest_data has "values" key, iterate through that. Otherwise, assume it's a list.
                
                results_list = manifest_data.get("values", [])
                for file_info in results_list:
                    if file_info.get("kind") == "Transcription" and file_info.get("name", "").endswith(".json"):
                        # Name check for .json is an assumption for the main transcript data
                        transcription_file_url = file_info.get("links", {}).get("contentUrl")
                        if transcription_file_url:
                            print(f"Found transcription file URL: {transcription_file_url}")
                            return transcription_file_url
                
                # Fallback or alternative structure if the above is not found
                if item.get("kind") == "transcription" and "contentUrl" in item: # Simpler structure
                     print(f"Found transcription file URL (direct): {item['contentUrl']}")
                     return item["contentUrl"]

        raise Exception("Transcription result URL not found in manifest.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching or parsing transcription manifest from {manifest_url}: {e}")
        raise
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from manifest {manifest_url}: {e}")
        raise


def _fetch_transcription_json_content(transcription_content_url: str) -> dict:
    """
    Fetches the JSON content of the transcription result.
    """
    print(f"Fetching transcription content from: {transcription_content_url}")
    try:
        # Similar to manifest, assuming contentUrl is accessible (e.g., SAS URL)
        response = requests.get(transcription_content_url)
        response.raise_for_status()
        content_json = response.json()
        return content_json
    except requests.exceptions.RequestException as e:
        print(f"Error fetching transcription JSON content from {transcription_content_url}: {e}")
        raise
    except json.JSONDecodeError as e:
        print(f"Error decoding transcription JSON content from {transcription_content_url}: {e}")
        raise

def _extract_display_text_from_azure_json(azure_result_json: dict) -> str:
    """
    Extracts all "display" text from the Azure transcription JSON.
    The structure for "recognizedPhrases" and "displayText" is assumed as per common Azure results.
    """
    print("Extracting display text from Azure JSON result.")
    full_text_parts = []
    
    # Azure Batch Transcription JSON has a structure like:
    # { "recognizedPhrases": [ { "nBest": [ { "display": "text..." } ], ... }, ... ] }
    # Or sometimes "combinedRecognizedPhrases"
    # Or results -> channel -> nBest -> display
    
    # Based on common Batch Transcription v3.1 output:
    # The JSON content from `contentUrl` (the actual transcript) often looks like:
    # {
    #   "source": "...",
    #   "timestamp": "...",
    #   "duration": "...",
    #   "recognizedPhrases": [
    #     {
    #       "recognitionStatus": "Success",
    #       "channel": 0, (or speakerId if diarization is on)
    #       "offset": "PT0S",
    #       "duration": "PT5S",
    #       "nBest": [
    #         {
    #           "confidence": 0.85,
    #           "lexical": "hello world",
    #           "itn": "hello world",
    #           "maskedITN": "hello world",
    #           "display": "Hello world."
    #         }
    #       ]
    #     },
    #     ...
    #   ]
    # }
    # The prompt specifically asks for "displayText" from "recognizedPhrases".

    recognized_phrases = azure_result_json.get("recognizedPhrases", [])
    if not recognized_phrases:
        # Check for alternative structures if the primary one is empty
        # For example, some Azure services might nest it differently or use a different key.
        # However, sticking to "recognizedPhrases" as per instruction for now.
        print("Warning: 'recognizedPhrases' array is empty or not found in the Azure JSON result.")
        return ""

    for phrase_info in recognized_phrases:
        # Each phrase_info could have multiple nBest alternatives
        n_best_alternatives = phrase_info.get("nBest", [])
        if n_best_alternatives:
            # We typically take the first (and usually best) alternative
            best_alternative = n_best_alternatives[0]
            display_text = best_alternative.get("display")
            if display_text:
                full_text_parts.append(display_text)
            else:
                # Fallback if 'display' is missing, though it shouldn't be for successful phrases
                lexical_text = best_alternative.get("lexical")
                if lexical_text:
                    print(f"Warning: 'display' text not found for a phrase, using 'lexical': {lexical_text}")
                    full_text_parts.append(lexical_text)
        else:
            # This case might occur if a segment couldn't be transcribed properly
             print(f"Warning: No 'nBest' alternatives found for a phrase: {phrase_info}")


    if not full_text_parts:
        print("Warning: No display text could be extracted from the Azure JSON.")
        return ""
        
    final_transcription = " ".join(full_text_parts).strip()
    print(f"Extracted transcription: {final_transcription[:200]}...") # Log snippet
    return final_transcription

# --- Main Transcription Function ---

def transcribe_audio_azure(audio_url: str, output_transcription_path: str, locale: str = "es-ES") -> str:
    """
    Transcribes an audio file using Azure Batch Transcription.

    Args:
        audio_url (str): Publicly accessible URL of the audio file.
        output_transcription_path (str): Path to save the final transcription text.
        locale (str): Locale of the audio (e.g., "es-ES", "en-US").

    Returns:
        str: The full transcription text.
    """
    print(f"Starting Azure transcription process for audio URL: {audio_url}")
    print(f"Output will be saved to: {output_transcription_path}")

    if not Config.AZURE_SPEECH_KEY or not Config.AZURE_SPEECH_ENDPOINT:
        raise ValueError("Azure Speech Key or Endpoint is not configured. Please check your .env file or Config.")

    try:
        # 1. Create transcription job
        status_url = _create_azure_transcription_job(audio_url, locale)

        # 2. Wait for transcription to complete
        status_payload = _wait_for_azure_transcription(status_url)

        # 3. Get the manifest URL from the status payload
        # The manifest URL (containing links to actual result files) is in status_payload.links.files
        manifest_url = status_payload.get("links", {}).get("files")
        if not manifest_url:
            raise Exception("Manifest URL ('links.files') not found in Azure transcription status payload.")
        print(f"Manifest URL obtained: {manifest_url}")

        # 4. Get the specific transcription file URL from the manifest
        # This function needs to fetch manifest_url and parse its JSON content
        transcription_file_info_url = _get_transcription_files_url_from_manifest(manifest_url)
        if not transcription_file_info_url: # Should be caught by the function, but double check
             raise Exception("Failed to get specific transcription file URL from manifest.")

        # 5. Fetch the actual transcription JSON content
        azure_result_json = _fetch_transcription_json_content(transcription_file_info_url)

        # 6. Extract the display text
        full_transcription_text = _extract_display_text_from_azure_json(azure_result_json)

        # 7. Save the transcription
        os.makedirs(os.path.dirname(output_transcription_path), exist_ok=True)
        with open(output_transcription_path, "w", encoding="utf-8") as file:
            file.write(full_transcription_text)
        
        print(f"Transcription saved successfully to {output_transcription_path}")
        return full_transcription_text

    except Exception as e:
        print(f"An error occurred during the Azure transcription process: {str(e)}")
        # Optionally, re-raise or handle more gracefully (e.g., return None or an error message)
        raise # Re-raising to make it clear the process failed

def main_test():
    """
    A simple main function for testing the Azure transcription process.
    Requires a publicly accessible audio URL.
    """
    print("Starting Azure Transcription Test...")

    # --- Configuration for testing ---
    # This should be a publicly accessible URL for Azure to fetch.
    # For local files, you'd typically upload them to Azure Blob Storage first
    # and then provide the SAS URL to the audio file here.
    # Example: test_audio_url = "YOUR_PUBLICLY_ACCESSIBLE_AUDIO_URL.wav" 
    # Ensure this URL points to a compatible audio format (WAV, MP3, etc.)
    
    # For demonstration, let's assume the audio URL is passed via an environment variable
    # or hardcoded if you are testing in a controlled environment.
    test_audio_url = os.getenv("TEST_AZURE_AUDIO_URL") 
    if not test_audio_url:
        print("Error: TEST_AZURE_AUDIO_URL environment variable not set.")
        print("Please set it to a publicly accessible audio URL to run the test.")
        # Example: test_audio_url = "https://yourblobstorage.blob.core.windows.net/container/audio.wav?sastoken"
        return

    # Define where to save the test transcription
    # Using Path for better cross-platform compatibility
    project_root = Path(__file__).resolve().parent.parent.parent
    output_dir = project_root / "data" / "output" / "transcriptions_azure_test"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a unique filename for the test output
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    output_file_path = output_dir / f"test_transcription_{timestamp}.txt"
    
    print(f"Test Audio URL: {test_audio_url}")
    print(f"Test Output Transcription Path: {output_file_path}")

    try:
        # Ensure Azure credentials are set in Config (implicitly checked by transcribe_audio_azure)
        if not Config.AZURE_SPEECH_KEY or not Config.AZURE_SPEECH_ENDPOINT:
            print("Error: Azure Speech Key or Endpoint not configured in Config.")
            print("Please ensure .env file is correctly set up and loaded by src/config.py.")
            return

        print(f"Using Azure Speech Endpoint: {Config.AZURE_SPEECH_ENDPOINT}")
        
        transcription = transcribe_audio_azure(
            audio_url=test_audio_url,
            output_transcription_path=str(output_file_path), # Ensure path is string
            locale="es-ES" # Example locale
        )
        print("\n--- Test Transcription Result ---")
        print(transcription)
        print(f"\nFull transcription saved to: {output_file_path}")

    except ValueError as ve: # Specific for config errors
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An error occurred during the test: {str(e)}")

if __name__ == "__main__":
    # This main_test() is for demonstration and testing.
    # In a real application, transcribe_audio_azure would be called by other modules.
    # To run this test, you would execute: python src/transcription/transcribe_audio.py
    # And ensure TEST_AZURE_AUDIO_URL is set in your environment.
    
    # Check if the script is run to execute the test
    # Simple check, can be made more robust if needed
    if os.getenv("RUN_AZURE_TRANSCRIPTION_TEST") == "true":
        main_test()
    else:
        print("This script is intended to be used as a module.")
        print("To run the test function main_test(), set the environment variable RUN_AZURE_TRANSCRIPTION_TEST=true")
        print("Example: RUN_AZURE_TRANSCRIPTION_TEST=true python src/transcription/transcribe_audio.py")
