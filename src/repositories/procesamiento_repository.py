from sqlalchemy.orm import Session
from sqlalchemy import text

def create_sesion_online(db: Session, data: dict) -> int:
    sql = text("""
        EXEC ia.sp_insert_sesion_online 
            @IdProgramaGeneral = :IdProgramaGeneral,
            @IdPEspecificoPadre = :IdPEspecificoPadre,
            @IdPEspecificoHijo = :IdPEspecificoHijo,
            @TipoPrograma = :TipoPrograma,
            @Sesion = :Sesion,
            @UrlVideo = :UrlVideo
    """)

    params = {
        "IdProgramaGeneral": data["IdProgramaGeneral"],
        "IdPEspecificoPadre": data.get("IdPEspecificoPadre"),
        "IdPEspecificoHijo": data.get("IdPEspecificoHijo"),
        "TipoPrograma": ",".join(map(str, data["TipoPrograma"]))
            if isinstance(data["TipoPrograma"], list) else data["TipoPrograma"],
        "Sesion": data["Sesion"],
        "UrlVideo": data["UrlVideo"],
    }

    # Execute the SP
    result = db.execute(sql, params)

    # **Fetch the result before committing**:
    row = result.fetchone()  # row is something like (123,) if your SP does SELECT 123
    db.commit()

    # If your SP returns SELECT SCOPE_IDENTITY() as InsertedID
    # then row = (InsertedID_value,)
    new_id = row[0] if row else None
    return new_id

def update_video_state(db: Session, sesion_id: int, success: bool, ruta: str):
    sql = text("""
        EXEC ia.sp_update_video_state 
            @Id = :id,
            @DescargaExitosa = :descargaExitosa,
            @RutaVideo = :rutaVideo
    """)
    params = {
        "id": sesion_id,
        "descargaExitosa": 1 if success else 0,
        "rutaVideo": ruta
    }
    db.execute(sql, params)
    db.commit()

def update_audio_extraction(db: Session, sesion_id: int, success: bool, audio_path: str):
    sql = text("""
        EXEC ia.sp_update_audio_extraction
            @Id = :id,
            @SeparacionVideo = :sepVideo,
            @AudioVideo = :audioPath
    """)

    params = {
        "id": sesion_id,
        "sepVideo": 1 if success else 0,
        "audioPath": audio_path
    }

    db.execute(sql, params)
    db.commit()

def update_transcription(db: Session, sesion_id: int, success: bool, transcript_text: str):
    sql = text("""
        EXEC ia.sp_update_transcription
            @Id = :id,
            @TranscripcionAudio = :transAudio,
            @TextoTranscripcion = :texto
    """)
    params = {
        "id": sesion_id,
        "transAudio": 1 if success else 0,
        "texto": transcript_text  # <-- the entire transcript
    }
    db.execute(sql, params)
    db.commit()

def update_summarization(db: Session, sesion_id: int, success: bool, summary_text: str):
    sql = text("""
        EXEC ia.sp_update_summarization
            @Id = :id,
            @Resumen = :resumen,
            @TextoResumen = :textoResumen
    """)
    params = {
        "id": sesion_id,
        "resumen": 1 if success else 0,
        "textoResumen": summary_text  # the entire summary
    }
    db.execute(sql, params)
    db.commit()
def insert_tipo_generar(db: Session, sesion_online_id: int, tipo: str) -> int:
    """
    Insert a row into T_ProcesamientoTipoGenerar for the given tipo.
    Returns the newly inserted Id.
    """
    sql = text("""
        EXEC ia.sp_insert_tipo_generar
            @IdProcesamientoSesionOnline = :sesionId,
            @Tipo = :tipo
    """)
    params = {
        "sesionId": sesion_online_id,
        "tipo": tipo
    }
    result = db.execute(sql, params)
    row = result.fetchone()  # e.g. (InsertedTipoGenerarID,)
    db.commit()
    return row[0] if row else None


def update_tipo_generar(db: Session, tipo_generar_id: int, registro_url: str, realizado: bool):
    """
    Update RegistroUrl and Realizado in T_ProcesamientoTipoGenerar.
    """
    sql = text("""
        EXEC ia.sp_update_tipo_generar
            @Id = :id,
            @RegistroUrl = :url,
            @Realizado = :done
    """)
    params = {
        "id": tipo_generar_id,
        "url": registro_url,
        "done": 1 if realizado else 0
    }
    db.execute(sql, params)
    db.commit()
    
def get_summary_text(db: Session, sesion_id: int) -> str:
    """
    Calls sp_get_summary_text to fetch TextoResumen from T_ProcesamientoSesionOnline.
    Returns the summary text (str) or None if not found.
    """
    sql = text("EXEC ia.sp_get_summary_text @Id = :id")
    params = {"id": sesion_id}

    result = db.execute(sql, params)
    row = result.fetchone()
    db.commit()  # If the SP doesn't modify anything, commit is optional, but safe

    if row:
        return row[0]  # The first column is TextoResumen
    return None