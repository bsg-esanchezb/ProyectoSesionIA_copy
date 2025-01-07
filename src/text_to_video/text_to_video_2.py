import requests
import time
import dotenv
import os

# API Configuration
API_KEY = os.getenv("HEYGEN_API_KEY")
TEMPLATE_ID = "44134ff53cf94c71a26467ccb7051efb"
headers = {
    "X-Api-Key": API_KEY,
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# Content Variables
TITLE = "Resumen Clase CRISP-DM"
TEMA_PRINCIPAL = "Resumen de la Clase sobre CRISP-DM y Modelado de Datos"
INTRODUCCION = ("La clase se centró en la segunda parte de CRISP-DM aplicada con R, con un enfoque práctico. "
               "Se revisaron las fases de CRISP-DM, que incluyen el entendimiento del negocio, entendimiento de los datos, "
               "preparación de los datos, modelado, evaluación y despliegue.")

# Subtema 1
SUBTEMA_1 = "Fases de CRISP-DM"
SUBTEMA_1_CLAVES = (
    "- Comprender el contexto y los objetivos del proyecto.\n"
    "- Examinar los datos disponibles y su calidad.\n"
    "- Involucra la limpieza, transformación y selección de variables.\n"
    "- Crear modelos utilizando técnicas de machine learning.\n"
    "- Medir la efectividad del modelo y su aplicabilidad al negocio.\n"
    "- Implementar el modelo en un entorno productivo y monitorear su rendimiento."
)
SUBTEMA_1_EXPLAYADO = ("Las fases de CRISP-DM incluyen el entendimiento del negocio, donde se comprendió el contexto "
                      "y los objetivos del proyecto. Luego, se pasó al entendimiento de los datos, examinando los datos "
                      "disponibles y su calidad. La preparación de los datos involucró la limpieza, transformación y "
                      "selección de variables. En la fase de modelado, se crearon modelos utilizando técnicas de machine "
                      "learning. La evaluación consistió en medir la efectividad del modelo y su aplicabilidad al negocio. "
                      "Finalmente, el despliegue implicó implementar el modelo en un entorno productivo y monitorear su "
                      "rendimiento.")

# Subtema 2
SUBTEMA_2 = "Insights de Minería de Datos"
SUBTEMA_2_CLAVES = (
    "- Las decisiones deben basarse en datos concretos.\n"
    "- Uso de conjuntos de datos de entrenamiento, validación y prueba.\n"
    "- Construir múltiples modelos para mejorar el rendimiento.\n"
    "- Cuestionar modelos perfectos para evitar el sobreajuste.\n"
    "- Monitorear el despliegue del modelo.\n"
    "- Comunicar hallazgos de manera efectiva."
)
SUBTEMA_2_EXPLAYADO = ("Se destacó la importancia de centrarse en los datos, ya que las decisiones deben basarse en "
                      "datos concretos. Se subrayó el uso de conjuntos de datos de entrenamiento, validación y prueba "
                      "como fundamental para construir y evaluar modelos. Construir múltiples modelos aumenta la "
                      "probabilidad de encontrar el mejor rendimiento. Se aconsejó cuestionar modelos perfectos para "
                      "evitar el sobreajuste. Además, se enfatizó la necesidad de monitorear el despliegue del modelo "
                      "para asegurar su correcto funcionamiento en producción y la importancia de comunicar hallazgos "
                      "de manera efectiva para la toma de decisiones.")

# Subtema 3
SUBTEMA_3 = "Conceptos Clave"
SUBTEMA_3_CLAVES = (
    "- Aprendizaje supervisado: Se entrena un modelo con datos etiquetados.\n"
    "- Aprendizaje no supervisado: Se busca patrones en datos no etiquetados."
)
SUBTEMA_3_EXPLAYADO = ("Se explicaron los conceptos de aprendizaje supervisado y no supervisado. En el aprendizaje "
                      "supervisado, se entrena un modelo con datos etiquetados, como en el caso de la clasificación. "
                      "Por otro lado, el aprendizaje no supervisado busca patrones en datos no etiquetados, como en "
                      "el clustering.")

# Presentación y Conclusiones
PRESENTACION_PRINCIPALES_TEMAS = ("Se presentaron las fases de CRISP-DM, insights importantes sobre la minería de datos, "
                                "y conceptos clave como el aprendizaje supervisado y no supervisado. Además, se "
                                "discutieron ejemplos prácticos de predicción de diabetes y clasificación de especies "
                                "de iris.")

CONCLUSIONES_EXPLAYADO = ("La metodología CRISP-DM proporcionó un marco estructurado para la minería de datos y el "
                         "modelado, lo cual es crucial para entender los datos y el contexto del negocio, permitiendo "
                         "desarrollar modelos efectivos. La evaluación continua y la comunicación de resultados fueron "
                         "esenciales para el éxito del análisis de datos, asegurando que los modelos sean aplicables "
                         "y útiles para la toma de decisiones en el entorno empresarial.")

CONCLUSION_CLAVES = (
    "- La metodología CRISP-DM proporciona un marco estructurado para la minería de datos y el modelado.\n"
    "- Es crucial entender los datos y el contexto del negocio para desarrollar modelos efectivos.\n"
    "- La evaluación continua y la comunicación de resultados son esenciales para el éxito del análisis de datos."
)

def create_payload():
    """Create the payload for the video generation API."""
    return {
        "test": False,
        "caption": False,
        "template_id": TEMPLATE_ID,
        "title": TITLE,
        "dimension": {
            "width": 1280,
            "height": 720
        },
        "variables": {
            "tema_principal": {"name": "tema_principal", "type": "text", "properties": {"content": TEMA_PRINCIPAL}},
            "introduccion": {"name": "introduccion", "type": "text", "properties": {"content": INTRODUCCION}},
            "subtema_1": {"name": "subtema_1", "type": "text", "properties": {"content": SUBTEMA_1}},
            "subtema_1_claves": {"name": "subtema_1_claves", "type": "text", "properties": {"content": SUBTEMA_1_CLAVES}},
            "subtema_1_explayado": {"name": "subtema_1_explayado", "type": "text", "properties": {"content": SUBTEMA_1_EXPLAYADO}},
            "subtema_2": {"name": "subtema_2", "type": "text", "properties": {"content": SUBTEMA_2}},
            "subtema_2_claves": {"name": "subtema_2_claves", "type": "text", "properties": {"content": SUBTEMA_2_CLAVES}},
            "subtema_2_explayado": {"name": "subtema_2_explayado", "type": "text", "properties": {"content": SUBTEMA_2_EXPLAYADO}},
            "subtema_3": {"name": "subtema_3", "type": "text", "properties": {"content": SUBTEMA_3}},
            "subtema_3_claves": {"name": "subtema_3_claves", "type": "text", "properties": {"content": SUBTEMA_3_CLAVES}},
            "subtema_3_explayado": {"name": "subtema_3_explayado", "type": "text", "properties": {"content": SUBTEMA_3_EXPLAYADO}},
            "presentacion_principales_temas": {"name": "presentacion_principales_temas", "type": "text", "properties": {"content": PRESENTACION_PRINCIPALES_TEMAS}},
            "conclusiones_explayado": {"name": "conclusiones_explayado", "type": "text", "properties": {"content": CONCLUSIONES_EXPLAYADO}},
            "conclusion_claves": {"name": "conclusion_claves", "type": "text", "properties": {"content": CONCLUSION_CLAVES}}
        }
    }

def generate_video():
    """Generate video using HeyGen API."""
    generate_url = f"https://api.heygen.com/v2/template/{TEMPLATE_ID}/generate"
    
    try:
        response = requests.post(generate_url, headers=headers, json=create_payload())
        response.raise_for_status()
        
        if not response.json().get("data"):
            print("Error:", response.json().get("error", "Unknown error"))
            return None
            
        return response.json()["data"]["video_id"]
    except requests.exceptions.RequestException as e:
        print(f"Error generating video: {str(e)}")
        return None

def check_video_status(video_id):
    """Check the status of video generation."""
    status_url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"
    
    while True:
        try:
            response = requests.get(status_url, headers=headers)
            response.raise_for_status()
            data = response.json()["data"]
            status = data["status"]

            if status == "completed":
                return data["video_url"], data["thumbnail_url"]
            elif status in ["processing", "pending"]:
                print("Video is still processing. Checking status...")
                time.sleep(5)
            elif status == "failed":
                print(f"Video generation failed. Error: {data.get('error', 'Unknown error')}")
                return None, None
        except requests.exceptions.RequestException as e:
            print(f"Error checking video status: {str(e)}")
            return None, None

def download_video(video_url, filename="generated_video.mp4"):
    """Download the generated video."""
    try:
        response = requests.get(video_url)
        response.raise_for_status()
        
        with open(filename, "wb") as video_file:
            video_file.write(response.content)
        print(f"Video successfully downloaded as {filename}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading video: {str(e)}")
        return False

def main():
    """Main function to orchestrate video generation process."""
    print("Starting video generation process...")
    
    # Generate video
    video_id = generate_video()
    if not video_id:
        return
    
    print(f"Video generation initiated. Video ID: {video_id}")
    
    # Check status and get URLs
    video_url, thumbnail_url = check_video_status(video_id)
    if not video_url:
        return
    
    print(f"Video generation completed!")
    print(f"Video URL: {video_url}")
    print(f"Thumbnail URL: {thumbnail_url}")
    
    # Download video
    download_video(video_url)

if __name__ == "__main__":
    main()