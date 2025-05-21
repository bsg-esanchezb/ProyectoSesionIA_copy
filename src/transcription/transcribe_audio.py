import os
import requests
import time
import json
from src.config import Config
from pathlib import Path

def transcribe_audio(audio_file_url: str, output_transcription_file_path: str) -> str:
    """
    Transcribe an audio file using Azure Speech-to-Text batch transcription.

    Args:
        audio_file_url (str): Publicly accessible URL of the audio file to transcribe.
                              Azure needs to be able to access this URL.
        output_transcription_file_path (str): Path to save the full JSON response from Azure.
                                               The extracted text will be returned by the function.

    Returns:
        str: The concatenated display text from the transcription.

    Raises:
        Exception: If any part of the transcription process fails.
    """
    print(f"Starting Azure batch transcription for: {audio_file_url}")

    azure_speech_key = Config.AZURE_SPEECH_KEY
    azure_speech_endpoint = Config.AZURE_SPEECH_ENDPOINT.replace("https://", "").replace("/", "") # Ensure correct format

    if not azure_speech_key:
        raise ValueError("AZURE_SPEECH_KEY is not configured.")
    if not azure_speech_endpoint:
        raise ValueError("AZURE_SPEECH_ENDPOINT is not configured.")

    # 1. Submit Transcription Job
    # Using API version 2024-11-15
    submit_url = f"https://{azure_speech_endpoint}/speechtotext/transcriptions?api-version=2024-11-15"
    
    headers = {
        "Ocp-Apim-Subscription-Key": azure_speech_key,
        "Content-Type": "application/json"
    }

    payload = {
        "contentUrls": [audio_file_url],
        "locale": "es-ES",  # Primary language specifier
        "displayName": f"batch-transcription-job-{Path(audio_file_url).stem}", # Dynamic display name
        "properties": {
            "wordLevelTimestampsEnabled": False # Verify if this is still supported and needed
            # "language": "es-ES", # Removed as locale is set at top level
            # Other properties like 'profanityFilterMode', 'punctuationMode' could be added here if needed.
        }
        # "locale": "es-ES" # Moved to top level
    }

    print(f"Submitting transcription job to: {submit_url}")
    try:
        response = requests.post(submit_url, headers=headers, json=payload)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        submission_response_json = response.json()
        status_url = submission_response_json.get("self")
        if not status_url:
            raise ValueError("Failed to get status URL from submission response.")
        print(f"Transcription job submitted. Status URL: {status_url}")
    except requests.exceptions.RequestException as e:
        print(f"Error submitting transcription job: {e}")
        if e.response is not None:
            print(f"Response content: {e.response.text}")
        raise
    except (ValueError, KeyError) as e:
        print(f"Error processing submission response: {e}")
        raise

    # 2. Poll for Status
    files_url = None
    max_retries = 60 # Poll for up to 30 minutes (60 retries * 30 seconds)
    retries = 0
    
    print("Polling for transcription status...")
    while retries < max_retries:
        try:
            status_response = requests.get(status_url, headers={"Ocp-Apim-Subscription-Key": azure_speech_key})
            status_response.raise_for_status()
            status_json = status_response.json()
            current_status = status_json.get("status")
            print(f"Current job status: {current_status} (Attempt {retries + 1}/{max_retries})")

            if current_status == "Succeeded":
                files_url = status_json.get("links", {}).get("files")
                if not files_url:
                     # For API version 2024-11-15, the files link structure should be similar.
                     # If issues arise, this is where to check Azure's response for the correct path to files.
                    raise ValueError("Could not find 'files' URL in successful job status.")
                print("Transcription job succeeded.")
                break
            elif current_status == "Failed":
                error_details = status_json.get("properties", {}).get("error", {})
                print(f"Transcription job failed. Error: {error_details}")
                raise Exception(f"Azure transcription failed: {error_details.get('message', 'Unknown error')}")
            elif current_status in ["Running", "NotStarted"]:
                time.sleep(30)  # Wait 30 seconds before polling again
                retries += 1
            else: # Unexpected status
                print(f"Unexpected job status: {current_status}")
                raise Exception(f"Unexpected Azure transcription status: {current_status}")

        except requests.exceptions.RequestException as e:
            print(f"Error polling status: {e}")
            # Depending on the error, you might want to retry or fail fast
            time.sleep(30) 
            retries += 1 
        except (ValueError, KeyError) as e:
            print(f"Error processing status response: {e}")
            raise


    if not files_url:
        raise Exception("Transcription job did not complete successfully or files URL not found after polling.")

    # 3. Retrieve Transcription
    print(f"Retrieving transcription files from: {files_url}")
    try:
        files_response = requests.get(files_url, headers={"Ocp-Apim-Subscription-Key": azure_speech_key})
        files_response.raise_for_status()
        files_json = files_response.json()
        
        transcription_content_url = None
        for file_info in files_json.get("values", []):
            if file_info.get("kind") == "transcription":
                transcription_content_url = file_info.get("links", {}).get("contentUrl")
                break
        
        if not transcription_content_url:
            raise ValueError("Could not find transcription file content URL in files response.")

        print(f"Downloading transcription from: {transcription_content_url}")
        transcription_result_response = requests.get(transcription_content_url) # No auth header needed for contentUrl usually
        transcription_result_response.raise_for_status()
        azure_response_json = transcription_result_response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error retrieving transcription files/result: {e}")
        raise
    except (ValueError, KeyError) as e:
        print(f"Error processing files response or transcription result: {e}")
        raise

    # 4. Save Full JSON Response
    output_dir = Path(output_transcription_file_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_transcription_file_path, "w", encoding="utf-8") as f:
        json.dump(azure_response_json, f, ensure_ascii=False, indent=4)
    print(f"Full Azure transcription JSON saved to: {output_transcription_file_path}")

    # 5. Extract Display Text
    # Based on typical Azure Speech API structure for combined result.
    # This logic should be robust for API version 2024-11-15 as well.
    # The key "combinedRecognizedPhrases" might not exist if the audio is too short or no speech is detected.
    # "recognizedPhrases" contains segment-level details.
    full_transcription = ""
    if "combinedRecognizedPhrases" in azure_response_json and azure_response_json["combinedRecognizedPhrases"]:
        full_transcription = azure_response_json["combinedRecognizedPhrases"][0].get("display", "")
    elif "recognizedPhrases" in azure_response_json: # Fallback to joining individual recognized phrases
        transcription_parts = []
        for phrase in azure_response_json["recognizedPhrases"]:
            # 'lexical' is often the most accurate, 'display' is formatted for readability
            transcription_parts.append(phrase.get("lexical", phrase.get("display", "")))
        full_transcription = " ".join(filter(None, transcription_parts))
    else:
        print("Warning: Could not find 'combinedRecognizedPhrases' or 'recognizedPhrases' in Azure response.")
        # This might happen for empty audio or if Azure returns an unexpected structure.

    print(f"Transcription extracted: '{full_transcription[:100]}...'") # Print a snippet
    return full_transcription.strip()

# def main():
#     """Main execution function - Example for testing (requires a public URL)"""
#     # This is an example and needs a publicly accessible audio URL.
#     # For local files, you'd need to upload them to a service like Azure Blob Storage first.
#     # example_audio_url = "YOUR_PUBLICLY_ACCESSIBLE_AUDIO_URL.mp3" # Or .wav, etc.
#     # example_output_json = "data/output/transcriptions/azure_transcription_output.json"
#     #
#     # # Ensure Config has AZURE_SPEECH_KEY and AZURE_SPEECH_ENDPOINT set in .env or environment
#     # if not Config.AZURE_SPEECH_KEY or not Config.AZURE_SPEECH_ENDPOINT:
#     #     print("Error: Azure Speech credentials (AZURE_SPEECH_KEY, AZURE_SPEECH_ENDPOINT) not configured.")
#     #     print("Please set them in your .env file or environment variables.")
#     #     return 1
#     #
#     # try:
#     #     print(f"Starting transcription for example URL: {example_audio_url}")
#     #     Path(example_output_json).parent.mkdir(parents=True, exist_ok=True) # Ensure output dir exists
#     #
#     #     transcribed_text = transcribe_audio(example_audio_url, example_output_json)
#     #     print("\n--- Full Transcribed Text ---")
#     #     print(transcribed_text)
#     #     print(f"\nFull Azure JSON response saved to: {example_output_json}")
#     #
#     # except ValueError as ve: # Specific for config errors
#     #     print(f"Configuration Error: {ve}")
#     #     return 1
#     # except Exception as e:
#     #     print(f"An error occurred during transcription: {str(e)}")
#     #     return 1
#     #
#     # return 0

# if __name__ == "__main__":
#     # Note: Running this directly requires Azure credentials and a public audio URL.
#     # exit_code = main()
#     # exit(exit_code)
    pass # Keep the file importable without running main automatically
