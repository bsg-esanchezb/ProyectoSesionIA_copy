import os
import re
import requests
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def download_vimeo_video(vimeo_url, download_directory, access_token):
    try:
        # Ensure the directory exists
        os.makedirs(download_directory, exist_ok=True)

        # Extract video ID and proceed as before
        video_id = re.search(r"vimeo\.com/(\d+)", vimeo_url)
        if not video_id:
            return {"success": False, "error": "Invalid Vimeo URL format."}
        video_id = video_id.group(1)

        # Fetch video metadata
        url = f"https://api.vimeo.com/videos/{video_id}"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        video_data = response.json()

        # Get download link
        files = video_data.get('files', [])
        if not files:
            return {"success": False, "error": "No downloadable files found."}
        download_link = min(files, key=lambda x: x.get('height', float('inf')))['link']

        # File path and download
        video_title = video_data.get("name", video_id)
        file_name = f"{re.sub(r'[^a-zA-Z0-9_]+', '_', video_title)}.mp4"
        file_path = os.path.join(download_directory, file_name)

        # Download video
        response = requests.get(download_link, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        with open(file_path, "wb") as f, tqdm(total=total_size, unit='B', unit_scale=True) as bar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    bar.update(len(chunk))
        
        return {"success": True, "file_path": file_path}
    except Exception as e:
        return {"success": False, "error": str(e)}
