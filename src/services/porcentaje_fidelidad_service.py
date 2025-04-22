from openai import OpenAI
from src.repositories.procesamiento_repository import update_porcentaje_fidelidad
from src import config

client = OpenAI(api_key=config.Config.OPENAI_API_KEY)

def evaluate_fidelity_with_llm(summary_text: str, script_text: str, db, sesion_id: int) -> int:
    prompt = f"""
Evalúa el resumen generado a partir de una transcripción, evaluando su fidelidad al contenido original. Proporciona una puntuación en porcentaje entre 1 y 100, donde 100 significa que el resumen refleja completamente el contenido teórico de la transcripción y 1 que no tiene relación alguna.

Resumen:
{summary_text}

Transcripción:
{script_text}

Pasos
Leer la Transcripción: Revisa cuidadosamente la transcripción de clase proporcionada.

Revisar el Resumen: Examina el resumen para evaluar su estructura, contenido y organización.
Comparación:

Compara los temas principales y subtemas mencionados en la transcripción con los del resumen, asegurando que se limiten al contenido teórico.

Verifica la fidelidad y relevancia del contenido del resumen respecto a la transcripción, comprobando que no aparezca contenido inventado.

Asegúrate de que no se omitan puntos críticos y que se mantenga la secuencia lógica.
Evaluar la Cobertura: Asegúrate de que el resumen cubra todos los puntos teóricos importantes discutidos en la transcripción.

Recuerda que es un resumen limitado, no puede abarcar todos los temas de la transcripción ya que de ser así ya no sería un resumen. Excluye temas personales o situaciones no académicas como la experiencia del docente.

Solo responde con un número entero entre 1 y 100. Nada más.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        output_text = response.choices[0].message.content.strip()
        fidelity_score = int("".join(filter(str.isdigit, output_text)))

        # Optional: save to DB
        update_porcentaje_fidelidad(db, sesion_id, fidelity_score)

        return fidelity_score

    except Exception as e:
        raise RuntimeError(f"Fidelity evaluation failed: {str(e)}")

if __name__ == "__main__":
    from pathlib import Path

    transcription_path = Path(r"C:\Users\esanchezb\Documents\ProyectoResumenSesionIA\data\output\transcriptions\prueba_2.txt")
    summary_path = Path(r"C:\Users\esanchezb\Documents\ProyectoResumenSesionIA\data\temp\summary\prueba_resumen_2.txt")

    with open(transcription_path, "r", encoding="utf-8", errors="replace") as f:
        transcription = f.read()

    with open(summary_path, "r", encoding="utf-8", errors="replace") as f:
        summary = f.read()

    score = evaluate_fidelity_with_llm(summary, transcription, sesion_id=None, db=None)
    print(f"Evaluated PorcentajeFidelidad: {score}")
