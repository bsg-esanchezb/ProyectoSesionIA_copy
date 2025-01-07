from download_video.download_video import download_vimeo_video

def download_video(vimeo_url: str, download_directory: str, access_token: str) -> str:
    """Downloads a video from Vimeo and returns the file path.

    Args:
        vimeo_url (str): URL of the Vimeo video to download.
        download_directory (str): Directory where the video should be saved.
        access_token (str): Vimeo API access token.

    Returns:
        str: File path of the downloaded video on success.

    Raises:
        Exception: If an error occurs during the download.
    """
    result = download_vimeo_video(vimeo_url, download_directory, access_token)
    if result["success"]:
        return result["file_path"]
    else:
        raise Exception(result["error"])
