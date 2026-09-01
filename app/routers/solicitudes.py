import sqlite3
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.database import obtener_conexion
from app import schemas, security

router = APIRouter(prefix="/solicitudes", tags=["Solicitudes de Adopción"])

# 1. Listar todas las solicitudes
@router.get("/", response_model=List[schemas.SolicitudAdopcionRespuesta])
def listar_solicitudes():
    conn = obtener_conexion()
    cursor = conn.cursor()
    solicitudes = cursor.execute(
        "SELECT id, animal_id, usuario_id, estado, fecha FROM solicitudes_adopcion"
    ).fetchall()
    conn.close()
    return [dict(s) for s in solicitudes]

# 2. Obtener una solicitud por ID
@router.get("/{solicitud_id}", response_model=schemas.SolicitudAdopcionRespuesta)
def obtener_solicitud(solicitud_id: int):
    conn = obtener_conexion()
    cursor = conn.cursor()
    solicitud = cursor.execute(
        "SELECT id, animal_id, usuario_id, estado, fecha FROM solicitudes_adopcion WHERE id = ?", 
        (solicitud_id,)
    ).fetchone()
    conn.close()
    
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    return dict(solicitud)

# 3. Crear solicitud de adopción
@router.post("/", response_model=schemas.SolicitudAdopcionRespuesta, status_code=status.HTTP_201_CREATED)
def crear_solicitud(
    solicitud: schemas.SolicitudAdopcionCrear,
    usuario_actual: dict = Depends(security.obtener_usuario_actual)
):
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    animal = cursor.execute("SELECT id FROM animales WHERE id = ?", (solicitud.animal_id,)).fetchone()
    if not animal:
        conn.close()
        raise HTTPException(status_code=404, detail="El animal especificado no existe")

    cursor.execute(
        "INSERT INTO solicitudes_adopcion (animal_id, usuario_id, estado, fecha) VALUES (?, ?, ?, ?)",
        (solicitud.animal_id, usuario_actual["id"], "Pendiente", str(solicitud.fecha))
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()
    
    return {
        "id": nuevo_id,
        "animal_id": solicitud.animal_id,
        "usuario_id": usuario_actual["id"],
        "estado": "Pendiente",
        "fecha": solicitud.fecha
    }

# 4. Actualizar estado de solicitud (Aprobar / Rechazar - Solo Admin)
@router.put("/{solicitud_id}/estado", response_model=schemas.SolicitudAdopcionRespuesta)
def cambiar_estado_solicitud(
    solicitud_id: int,
    nuevo_estado: str,
    admin_actual: dict = Depends(security.requerir_admin)
):
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE solicitudes_adopcion SET estado = ? WHERE id = ?",
        (nuevo_estado, solicitud_id)
    )
    afectados = cursor.rowcount
    
    if afectados == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
        
    conn.commit()
    solicitud = cursor.execute(
        "SELECT id, animal_id, usuario_id, estado, fecha FROM solicitudes_adopcion WHERE id = ?", 
        (solicitud_id,)
    ).fetchone()
    conn.close()
    
    return dict(solicitud)

# 5. Eliminar solicitud (Solo Admin)
@router.delete("/{solicitud_id}", status_code=status.HTTP_200_OK)
def eliminar_solicitud(
    solicitud_id: int,
    admin_actual: dict = Depends(security.requerir_admin)
):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM solicitudes_adopcion WHERE id = ?", (solicitud_id,))
    afectados = cursor.rowcount
    conn.commit()
    conn.close()

    if afectados == 0:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    return {"mensaje": f"Solicitud {solicitud_id} eliminada correctamente"}