from sqlalchemy.orm import Session
from sqlalchemy import text

def create_sesion_online(db: Session, data: dict) -> int:
    """
    Insert into T_ProcesamientoSesionOnline if not exists,
    or return existing Id if (IdPEspecifico, IdPEspecificoSesion, UrlVideo)
    is already in DB.
    """
    # 1) Verificación previa
    sql_check = text("""
        SELECT TOP 1 Id
        FROM [ia].[T_ProcesamientoSesionOnline]
        WHERE IdPEspecifico = :idEsp
          AND IdPEspecificoSesion = :idEspSes
          AND UrlVideo = :urlVid
    """)
    params_check = {
        "idEsp": data["IdPEspecifico"],
        "idEspSes": data.get("IdPEspecificoSesion"),
        "urlVid": data["UrlVideo"]
    }
    row_check = db.execute(sql_check, params_check).fetchone()
    if row_check:
        existing_id = row_check[0]
        db.commit()  # o db.rollback(), si prefieres
        return existing_id

    # 2) Convertir TipoResumenGrabacionOnline a string
    tipo_resumen_value = data.get("TipoResumenGrabacionOnline", "")
    if isinstance(tipo_resumen_value, list):
        # Convierto la lista [1, 3] en algo como "1,3" (sin espacios).
        # O "1, 3" si te acomoda. Solo asegúrate que sea un string válido para tu SP.
        tipo_resumen_str = ",".join(str(x) for x in tipo_resumen_value)
    else:
        # Si ya viene como string, lo tomas tal cual
        tipo_resumen_str = str(tipo_resumen_value)

    # 3) Insertar (vía SP)
    sql_insert = text("""
        EXEC ia.sp_insert_sesion_online
            @IdPEspecifico               = :idEsp,
            @IdPEspecificoSesion         = :idEspSes,
            @TipoResumenGrabacionOnline  = :tipoRes,
            @Sesion                      = :sesion,
            @UrlVideo                    = :urlVid
    """)
    params_insert = {
        "idEsp": data["IdPEspecifico"],
        "idEspSes": data.get("IdPEspecificoSesion"),
        "tipoRes": tipo_resumen_str,   # <--- Usar la variable convertida
        "sesion": data["Sesion"],
        "urlVid": data["UrlVideo"]
    }
    result_insert = db.execute(sql_insert, params_insert)
    row_insert = result_insert.fetchone()
    db.commit()

    new_id = row_insert[0] if row_insert else None
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