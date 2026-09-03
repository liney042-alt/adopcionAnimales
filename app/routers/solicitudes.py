from fastapi import APIRouter, HTTPException, Depends, status
import sqlite3
from app.database import obtener_conexion
from app import schemas, security

router = APIRouter(prefix="/solicitudes", tags=["Solicitudes de Adopción"])

@router.get("/", response_model=list[schemas.SolicitudRespuesta])
def listar_solicitudes(usuario_actual: dict = Depends(security.obtener_usuario_actual)):
    conn = obtener_conexion()
    cursor = conn.cursor()
    if usuario_actual.get("rol_id") == 1:
        cursor.execute("SELECT * FROM solicitudes")
    else:
        cursor.execute("SELECT * FROM solicitudes WHERE usuario_id = ?", (usuario_actual["sub"],))
    solicitudes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return solicitudes

@router.post("/", response_model=schemas.SolicitudRespuesta, status_code=status.HTTP_201_CREATED)
def crear_solicitud(
    solicitud: schemas.SolicitudCrear,
    usuario_actual: dict = Depends(security.obtener_usuario_actual)
):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO solicitudes (usuario_id, animal_id, estado, fecha) VALUES (?, ?, ?, ?)",
        (usuario_actual["sub"], solicitud.animal_id, "Pendiente", solicitud.fecha)
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()
    return {"id": nuevo_id, "usuario_id": int(usuario_actual["sub"]), "animal_id": solicitud.animal_id, "estado": "Pendiente", "fecha": solicitud.fecha}

@router.delete("/{solicitud_id}", status_code=status.HTTP_200_OK)
def eliminar_solicitud(
    solicitud_id: int,
    admin: dict = Depends(security.requerir_admin)
):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM solicitudes WHERE id = ?", (solicitud_id,))
    afectados = cursor.rowcount
    conn.commit()
    conn.close()

    if afectados == 0:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    return {"mensaje": f"Solicitud con ID {solicitud_id} eliminada correctamente"}