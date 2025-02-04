from sqlalchemy.orm import Session
from sqlalchemy import text

def create_sesion_online(db: Session, data: dict) -> int:
    """
    Inserta en T_ProcesamientoSesionOnline usando el SP sp_insert_sesion_online,
    ahora con las columnas renombradas:
      - IdPEspecifico
      - IdPEspecificoSesion
      - TipoResumenGrabacionOnline
      - (Sesion, UrlVideo se mantienen igual)
    """
    sql = text("""
        EXEC ia.sp_insert_sesion_online 
            @IdPEspecifico = :IdPEspecifico,
            @IdPEspecificoSesion = :IdPEspecificoSesion,
            @TipoResumenGrabacionOnline = :TipoResumenGrabacionOnline,
            @Sesion = :Sesion,
            @UrlVideo = :UrlVideo
    """)

    # Convertimos el array de ints a string (si viene así):
    # Antes teníamos "TipoPrograma". Ahora se llama "TipoResumenGrabacionOnline"
    tipo_resumen_str = data["TipoResumenGrabacionOnline"]
    if isinstance(tipo_resumen_str, list):
        tipo_resumen_str = ",".join(map(str, tipo_resumen_str))

    params = {
        "IdPEspecifico": data["IdPEspecifico"],
        "IdPEspecificoSesion": data.get("IdPEspecificoSesion"),
        "TipoResumenGrabacionOnline": tipo_resumen_str,
        "Sesion": data["Sesion"],
        "UrlVideo": data["UrlVideo"],
    }

    # Ejecutamos el SP
    result = db.execute(sql, params)
    row = result.fetchone()
    db.commit()

    new_id = row[0] if row else None
    return new_id


def update_video_state(db: Session, sesion_id: int, success: bool, ruta: str):
    sql = text("""
        EXEC ia.sp_update_video_state 
            @IdSesionOnline = :id,
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
            @IdSesionOnline = :id,
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
            @IdSesionOnline = :id,
            @TranscripcionAudio = :transAudio,
            @TextoTranscripcion = :texto
    """)
    params = {
        "id": sesion_id,
        "transAudio": 1 if success else 0,
        "texto": transcript_text
    }
    db.execute(sql, params)
    db.commit()


def update_summarization(db: Session, sesion_id: int, success: bool, summary_text: str):
    sql = text("""
        EXEC ia.sp_update_summarization
            @IdSesionOnline = :id,
            @Resumen = :resumen,
            @TextoResumen = :textoResumen
    """)
    params = {
        "id": sesion_id,
        "resumen": 1 if success else 0,
        "textoResumen": summary_text
    }
    db.execute(sql, params)
    db.commit()


def insert_tipo_generar(db: Session, sesion_online_id: int, id_resumen_grabacion_online: int) -> int:
    """
    Insert a row into T_ProcesamientoTipoGenerar, 
    ahora usando la columna IdResumenGrabacionOnline (INT) en vez de 'Tipo' (string).
    Returns the newly inserted Id.
    """
    sql = text("""
        EXEC ia.sp_insert_tipo_generar
            @IdProcesamientoSesionOnline = :sesionId,
            @IdResumenGrabacionOnline = :idResumen
    """)
    params = {
        "sesionId": sesion_online_id,
        "idResumen": id_resumen_grabacion_online
    }
    result = db.execute(sql, params)
    row = result.fetchone()
    db.commit()
    return row[0] if row else None


def update_tipo_generar(db: Session, tipo_generar_id: int, registro_url: str, realizado: bool):
    """
    Update RegistroUrl and Realizado in T_ProcesamientoTipoGenerar.
    """
    sql = text("""
        EXEC ia.sp_update_tipo_generar
            @IdTipoGenerar = :id,
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
    db.commit()

    if row:
        return row[0]  # The first column is TextoResumen
    return None

def get_pe_sesion_value(db: Session, sesion_id: int) -> int | None:
    """
    Devuelve el valor de IdPEspecificoSesion para un registro en T_ProcesamientoSesionOnline.
    """
    sql = text("""
        SELECT IdPEspecificoSesion
        FROM [ia].[T_ProcesamientoSesionOnline]
        WHERE Id = :id
    """)
    result = db.execute(sql, {"id": sesion_id})
    row = result.fetchone()
    return row[0] if row else None