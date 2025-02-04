# src/services/blob_service.py
import os
from azure.storage.blob import BlobServiceClient, ContentSettings
from pathlib import Path
from src.config import Config

def upload_file_to_blob(
    local_path: str,
    container_name: str = None,
    blob_subfolder: str = None
) -> str:
    """
    Uploads a local file to Azure Blob Storage.
    Returns the public URL (or SAS URL) of the uploaded blob if it's accessible,
    or the blob path if not configured for public access.
    """

    # 1) Crear el BlobServiceClient a partir de la connection string
    blob_service_client = BlobServiceClient.from_connection_string(
        Config.AZURE_BLOB_CONNECTION_STRING
    )

    container_name = container_name or Config.AZURE_BLOB_CONTAINER
    # subcarpeta opcional dentro del contenedor
    blob_subfolder = blob_subfolder or ""

    local_file = Path(local_path)
    if not local_file.is_file():
        raise FileNotFoundError(f"File not found: {local_file}")

    # 2) Construir el nombre final del blob: p.ej. "PDFs/123_20250131_study_guide.pdf"
    blob_name = (
        f"{blob_subfolder.strip('/')}/{local_file.name}"
        if blob_subfolder
        else local_file.name
    )
    # Quitar un posible "//" si subcarpeta va vacía
    blob_name = blob_name.lstrip("/")

    # 3) Obtener el cliente de blob
    blob_client = blob_service_client.get_blob_client(
        container=container_name,
        blob=blob_name
    )

    # 4) Definir content_settings opcionales, p.ej. si es PDF
    content_settings = None
    if local_file.suffix.lower() == ".pdf":
        content_settings = ContentSettings(content_type='application/pdf')
    elif local_file.suffix.lower() in [".wav", ".mp3"]:
        content_settings = ContentSettings(content_type='audio/wav')

    # 5) Subir el archivo
    with open(local_file, "rb") as data:
        blob_client.upload_blob(data, overwrite=True, content_settings=content_settings)

    # 6) Construir la URL pública o al menos la ruta
    # - Si tu contenedor está configurado como "blob (public read)" obtendrás una URL accesible
    blob_url = f"{blob_client.url}"

    return blob_url