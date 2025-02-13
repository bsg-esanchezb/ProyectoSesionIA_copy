from sqlalchemy.orm import Session
from sqlalchemy import text

def create_sesion_online(db: Session, data: dict) -> int:
    """
    Inserts into T_ProcesamientoSesionOnline if not exists,
    or returns the existing Id if a record with the same
    IdPEspecificoSesion and UrlVideo already exists.
    """
    # 1) Check for existing record (using only fields that still exist)
    sql_check = text("""
        SELECT TOP 1 Id
        FROM [ia].[T_ProcesamientoSesionOnline]
        WHERE IdPEspecificoSesion = :idEspSes
          AND UrlVideo = :urlVid
    """)
    params_check = {
        "idEspSes": data.get("IdPEspecificoSesion"),
        "urlVid": data["UrlVideo"]
    }
    row_check = db.execute(sql_check, params_check).fetchone()
    if row_check:
        existing_id = row_check[0]
        db.commit()
        return existing_id

    # 2) Insert the record via SP (note: we no longer send IdPEspecifico or TipoResumenGrabacionOnline)
    sql_insert = text("""
        EXEC ia.SP_TProcesamientoSesionOnline_Insertar
            @IdPEspecificoSesion = :idEspSes,
            @Sesion = :sesion,
            @UrlVideo = :urlVid,
            @UsuarioCreacion = :usuario,
            @UsuarioModificacion = :usuario
    """)
    params_insert = {
        "idEspSes": data.get("IdPEspecificoSesion"),
        "sesion": data["Sesion"],
        "urlVid": data["UrlVideo"],
        "usuario": data["Usuario"]  # This field must be present in the request
    }
    result_insert = db.execute(sql_insert, params_insert)
    row_insert = result_insert.fetchone()
    db.commit()

    new_id = row_insert[0] if row_insert else None
    return new_id

def update_video_state(db: Session, sesion_id: int, success: bool, ruta: str):
    sql = text("""
        EXEC ia.SP_TProcesamientoSesionOnline_ActualizarEstadoVideo
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
        EXEC ia.SP_TProcesamientoTipoGenerar_ActualizarExtraccionAudio
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
        EXEC ia.SP_TProcesamientoSesionOnline_ActualizarTranscripcion
            @Id = :id,
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
        EXEC ia.SP_TProcesamientoSesionOnline_ActualizarResumen
            @Id = :id,
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
        EXEC ia.SP_TProcesamientoTipoGenerar_Insertar
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
        EXEC ia.SP_TProcesamientoTipoGenerar_ActualizarTipoGenerar
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
    Calls SP_ObtenerTextoResumen to fetch TextoResumen from T_ProcesamientoSesionOnline.
    Returns the summary text (str) or None if not found.
    """
    sql = text("EXEC ia.SP_ObtenerTextoResumen @Id = :id")
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