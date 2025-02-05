from src.repositories.procesamiento_repository import (
    update_video_state,
    get_pe_sesion_value,
    update_audio_extraction,
    update_transcription,
    update_summarization,
    insert_tipo_generar,
    update_tipo_generar
)
from src.config import Config
from src.services.video_service import download_video
from src.services.audio_service import extract_audio
from src.services.transcription_service import transcribe_audio_file
from src.services.summarization_service import summarize_transcription
from src.services.study_guide_service import generate_study_guide_pdf
from src.services.concept_map_service import generate_concept_map_file
from src.services.podcast_service import generate_podcast
from src.services.blob_service import upload_file_to_blob
import os

def orchestrate_big_workflow(sesion_id: int, data: dict, db) -> dict:
    """
    Orchestrates the entire flow starting from an already created main record.
    Expects a pre-inserted session ID (sesion_id) and performs:
      1) Video download -> update DB
      2) Audio extraction -> update DB
      3) Transcription -> update DB
      4) Summarization -> update DB
      5) Insertion of artifact rows in T_ProcesamientoTipoGenerar
      6) Generation of final artifacts with unique timestamp-based filenames
    """
    # 2) Download video
    print("2) Download video")
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
    print("3) Extract audio")
    try:
        audio_path = extract_audio(video_path)
        update_audio_extraction(db, sesion_id, success=True, audio_path=audio_path)
    except Exception as e:
        update_audio_extraction(db, sesion_id, success=False, audio_path=None)
        raise Exception(f"Audio extraction failed: {str(e)}")

    # 4) Transcription
    print("4) Transcription")
    try:
        transcript_text, transcript_file_path = transcribe_audio_file(str(audio_path))
        update_transcription(db, sesion_id, success=True, transcript_text=transcript_text)
    except Exception as e:
        update_transcription(db, sesion_id, success=False, transcript_text=None)
        raise Exception(f"Transcription failed: {str(e)}")

    # 5) Summarize
    print("5) Summarize")
    try:
        summary_text, summary_file_path = summarize_transcription(transcript_file_path)
        update_summarization(db, sesion_id, success=True, summary_text=summary_text)
    except Exception as e:
        update_summarization(db, sesion_id, success=False, summary_text=None)
        raise Exception(f"Summarization failed: {str(e)}")

    # Obtain the value for IdPEspecificoSesion from the main record.
    pe_sesion_val = get_pe_sesion_value(db, sesion_id)

    # 6) Insert artifact rows (for optional artifacts)
    print("6) Insert rows in T_ProcesamientoTipoGenerar for optional artifacts")
    tipo_list = data.get("TipoResumenGrabacionOnline", [])
    # Mapping: 1 => PDF, 2 => ConceptMap, 3 => Podcast.
    tipos_mapping = {1: "PDF", 2: "ConceptMap", 3: "Podcast"}
    artifact_ids = {}
    for tipo_id in tipo_list:
        row_id = insert_tipo_generar(db, sesion_id, tipo_id)
        tipo_str = tipos_mapping.get(tipo_id, f"Unknown_{tipo_id}")
        artifact_ids[tipo_str] = row_id

    # 7) Generate final artifacts (using timestamp-based filenames)
    print("7) Generate final artifacts (using timestamp-based filenames inside each service)")

    # PDF Artifact
    print("PDF")
    if "PDF" in artifact_ids:
        pdf_id = artifact_ids["PDF"]
        try:
            pdf_path = generate_study_guide_pdf(summary_text=summary_text, pe_sesion_val=pe_sesion_val)
            pdf_blob_url = upload_file_to_blob(
                local_path=pdf_path,
                blob_subfolder=Config.AZURE_BLOB_SUBFOLDER_PDFS
            )
            update_tipo_generar(db, pdf_id, pdf_blob_url, realizado=True)
            os.remove(pdf_path)
        except Exception as e:
            update_tipo_generar(db, pdf_id, None, realizado=False)
            raise e

    # Concept Map Artifact
    print("Concept Map")
    if "ConceptMap" in artifact_ids:
        cm_id = artifact_ids["ConceptMap"]
        try:
            cm_path = generate_concept_map_file(summary_text=summary_text, pe_sesion_val=pe_sesion_val)
            update_tipo_generar(db, cm_id, cm_path, realizado=True)
        except Exception as e:
            update_tipo_generar(db, cm_id, None, realizado=False)
            raise e

    # Podcast Artifact
    print("Podcast")
    if "Podcast" in artifact_ids:
        pod_id = artifact_ids["Podcast"]
        try:
            podcast_result = generate_podcast(summary_text=summary_text, pe_sesion_val=pe_sesion_val)
            local_audio_path = podcast_result["audio_output"]
            audio_blob_url = upload_file_to_blob(
                local_path=local_audio_path,
                blob_subfolder=Config.AZURE_BLOB_SUBFOLDER_AUDIO
            )
            update_tipo_generar(db, pod_id, audio_blob_url, realizado=True)
            os.remove(local_audio_path)
        except Exception as e:
            update_tipo_generar(db, pod_id, None, realizado=False)
            raise e

    return {"message": "Workflow completed successfully", "sesion_id": sesion_id}
