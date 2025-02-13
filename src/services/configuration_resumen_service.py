import requests
from urllib.parse import urlencode
from src.config import Config

def enviar_resumen(id_pepecifico: int):
    base_url = Config.CONFIGURACION_RESUMENGRABACION_URL
    query_params = {'idPEspecifico': id_pepecifico}
    url = f"{base_url}?{urlencode(query_params)}"
    
    response = requests.post(url)
    response.raise_for_status()
    return response.json()
