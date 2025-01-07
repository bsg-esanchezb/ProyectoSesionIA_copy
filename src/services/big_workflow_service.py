# src/services/big_workflow_service.py

from repositories.procesamiento_repository import (
    create_sesion_online,
    update_video_state,
    update_audio_extraction,
    update_transcription,
    update_summarization,
    insert_tipo_generar,
    update_tipo_generar
)
from database import SessionLocal
from config import Config
from services.video_service import download_video
from services.audio_service import extract_audio
from services.transcription_service import transcribe_audio_file
from services.summarization_service import summarize_transcription
from services.study_guide_service import generate_study_guide_pdf
from services.concept_map_service import generate_concept_map_file
from services.podcast_service import generate_podcast

def orchestrate_big_workflow(data: dict, db: SessionLocal) -> dict:
    """
    Orchestrates the entire flow:
      1) Insert in T_ProcesamientoSesionOnline
      2) Download video -> update DB
      3) Extract audio -> update DB
      4) Transcription -> store in DB
      5) Summarize -> store in DB
      6) Insert rows in T_ProcesamientoTipoGenerar for optional artifacts (PDF, ConceptMap, Podcast)
      7) Generate each artifact with a unique timestamp-based filename
    """

    # 1) Insert main record
    sesion_id = create_sesion_online(db, data)

    # 2) Download video
    try:
        video_path = download_video(
            vimeo_url=data["UrlVideo"],
            download_directory=str(Config.INPUT_VIDEO_DIR),
            access_token=Config.VIMEO_ACCESS_TOKEN
        )
        update_video_state(db, sesion_id, success=True, ruta=video_path)
    except Exception as e:
        update_video_state(db, sesion_id, success=False, ruta=None)
        raise Exception(f"Download video failed: {str(e)}")

    # 3) Extract audio
    try:
        audio_path = extract_audio(video_path)
        update_audio_extraction(db, sesion_id, success=True, audio_path=audio_path)
    except Exception as e:
        update_audio_extraction(db, sesion_id, success=False, audio_path=None)
        raise Exception(f"Audio extraction failed: {str(e)}")

    # 4) Transcription
    try:
        transcript_text, transcript_file_path = transcribe_audio_file(str(audio_path))
        update_transcription(db, sesion_id, success=True, transcript_text=transcript_text)
    except Exception as e:
        update_transcription(db, sesion_id, success=False, transcript_text=None)
        raise Exception(f"Transcription failed: {str(e)}")

    # 5) Summarize
    try:
        summary_text, summary_file_path = summarize_transcription(transcript_file_path)
        update_summarization(db, sesion_id, success=True, summary_text=summary_text)
    except Exception as e:
        update_summarization(db, sesion_id, success=False, summary_text=None)
        raise Exception(f"Summarization failed: {str(e)}")

    # 6) Insert rows in T_ProcesamientoTipoGenerar for optional artifacts
    tipo_programa = data.get("TipoPrograma", [])
    tipos_mapping = {1: "PDF", 2: "ConceptMap", 3: "Podcast"}
    artifact_ids = {}

    for tipo_id in tipo_programa:
        tipo_str = tipos_mapping.get(tipo_id)
        if tipo_str:
            row_id = insert_tipo_generar(db, sesion_id, tipo_str)
            artifact_ids[tipo_str] = row_id

    # 7) Generate final artifacts (using timestamp-based filenames inside each service)
    # PDF
    if "PDF" in artifact_ids:
        pdf_id = artifact_ids["PDF"]
        try:
            pdf_path = generate_study_guide_pdf(summary_text=summary_text)
            update_tipo_generar(db, pdf_id, pdf_path, realizado=True)
        except Exception as e:
            update_tipo_generar(db, pdf_id, None, realizado=False)
            raise e

    # Concept Map
    if "ConceptMap" in artifact_ids:
        cm_id = artifact_ids["ConceptMap"]
        try:
            cm_path = generate_concept_map_file(summary_text=summary_text)
            update_tipo_generar(db, cm_id, cm_path, realizado=True)
        except Exception as e:
            update_tipo_generar(db, cm_id, None, realizado=False)
            raise e

    # Podcast
    if "Podcast" in artifact_ids:
        pod_id = artifact_ids["Podcast"]
        try:
            podcast_result = generate_podcast(summary_text=summary_text)
            update_tipo_generar(db, pod_id, podcast_result["audio_output"], realizado=True)
        except Exception as e:
            update_tipo_generar(db, pod_id, None, realizado=False)
            raise e

    return {"message": "Workflow completed successfully", "sesion_id": sesion_id}
