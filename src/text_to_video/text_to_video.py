import requests
import json
import os


class HeyGenVideoCreator:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            'x-api-key': self.api_key,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def upload_file(self, file_path):
        """
        Uploads a file (audio or image) to HeyGen and returns the URL and asset ID.
        """
        upload_endpoint = "https://upload.heygen.com/v1/asset"
        file_extension = os.path.splitext(file_path)[1].lower()

        # Determine content type
        content_type = {
            '.mp3': "audio/mpeg",
            '.wav': "audio/x-wav",
            '.m4a': "audio/mp4",
            '.png': "image/png",
            '.jpg': "image/jpeg",
            '.jpeg': "image/jpeg"
        }.get(file_extension, None)

        if not content_type:
            print(f"Unsupported file type: {file_extension}")
            return None

        upload_headers = {
            "x-api-key": self.api_key,
            "Content-Type": content_type
        }

        try:
            with open(file_path, "rb") as f:
                response = requests.post(upload_endpoint, data=f, headers=upload_headers)
                response.raise_for_status()
                upload_data = response.json()
                return {
                    'url': upload_data['data'].get('url'),
                    'asset_id': upload_data['data'].get('id')
                } if 'data' in upload_data else None

        except Exception as e:
            print(f"Error uploading file: {e}")
            return None

    def create_video(self, avatar_id, audio_url=None, input_text=None, scale=1.0, offset_x=0.0, offset_y=0.0,
                     avatar_style="normal", matting=False, circle_background_color=None,
                     background_asset_id=None, video_width=1280, video_height=720, test=False):
        """
        Creates a video using either text-to-speech or uploaded audio, with complete character configuration.
        """
        endpoint = 'https://api.heygen.com/v2/video/generate'

        if not background_asset_id:
            print("Background asset ID is required.")
            return None

        # Build character configuration
        character_config = {
            "type": "avatar",
            "avatar_id": avatar_id,
            "scale": scale,
            "avatar_style": avatar_style,
            "offset": {
                "x": offset_x,
                "y": offset_y
            }
        }

        if matting:
            character_config["matting"] = matting
        if circle_background_color and avatar_style == "circle":
            character_config["circle_background_color"] = circle_background_color

        # Build voice configuration
        voice_config = {}
        if audio_url:
            voice_config = {
                "type": "audio",
                "audio_url": audio_url
            }
        elif input_text:
            voice_config = {
                "type": "text",
                "input_text": input_text
            }
        else:
            print("Either audio_url or input_text must be provided.")
            return None

        payload = {
            "video_inputs": [
                {
                    "character": character_config,
                    "voice": voice_config,
                    "background": {
                        "type": "image",
                        "image_asset_id": background_asset_id
                    }
                }
            ],
            "dimension": {
                "width": video_width,
                "height": video_height
            },
            "test": test
        }

        try:
            response = requests.post(endpoint, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error creating video: {e}")
            return None


# Example usage
if __name__ == "__main__":
    API_KEY = "MzYxMDU0ZjY2OTUxNDc1YTkzZDg0ZjczNjNjN2RjZGQtMTcyMTY2NTA3OA=="  # Replace with your actual API key
    creator = HeyGenVideoCreator(API_KEY)

    # Paths to assets
    audio_path = r"C:\Users\esanchezb\Documents\Project_cafe_v2\data\output\podcast\multi_voices\podcast_es-US-Neural2-C_test-[AudioTrimmer.com].wav"
    image_path = r"C:\Users\esanchezb\Documents\Project_cafe_v2\data\input\images\logo_bsg.png"

    # Upload assets
    print("Uploading audio...")
    audio_upload = creator.upload_file(audio_path)
    audio_url = audio_upload['url'] if audio_upload else None

    print("Uploading background image...")
    image_upload = creator.upload_file(image_path)
    background_asset_id = image_upload['asset_id'] if image_upload else None

    # Create video with complete character configuration
    if audio_url and background_asset_id:
        print("Creating video...")
        response = creator.create_video(
            avatar_id="dba10ab69444486088791647836e0efe",
            audio_url=audio_url,
            scale=1.0,
            offset_x=-0.3,
            offset_y=0.0,
            avatar_style="normal",
            background_asset_id=background_asset_id,
            video_width=1280,
            video_height=720,
            test=False
        )

        if response and 'data' in response:
            print(f"Video created successfully! Video ID: {response['data']['video_id']}")
        else:
            print("Failed to create video.")
    else:
        print("Failed to upload required assets.")
