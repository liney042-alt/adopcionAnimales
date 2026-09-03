from fastapi import APIRouter, HTTPException, Depends, status
import sqlite3
from app.database import obtener_conexion
from app import schemas, security

router = APIRouter(prefix="/seguimientos", tags=["Seguimientos"])

@router.get("/", response_model=list[schemas.SeguimientoRespuesta])
def listar_seguimientos(usuario_actual: dict = Depends(security.obtener_usuario_actual)):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM seguimientos")
    seguimientos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return seguimientos

@router.post("/", response_model=schemas.SeguimientoRespuesta, status_code=status.HTTP_201_CREATED)
def crear_seguimiento(
    seguimiento: schemas.SeguimientoCrear,
    admin: dict = Depends(security.requerir_admin)
):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO seguimientos (adopcion_id, fecha, observaciones) VALUES (?, ?, ?)",
        (seguimiento.adopcion_id, seguimiento.fecha, seguimiento.observaciones)
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()
    return {**seguimiento.model_dump(), "id": nuevo_id}

@router.delete("/{seguimiento_id}", status_code=status.HTTP_200_OK)
def eliminar_seguimiento(
    seguimiento_id: int,
    admin: dict = Depends(security.requerir_admin)
):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM seguimientos WHERE id = ?", (seguimiento_id,))
    afectados = cursor.rowcount
    conn.commit()
    conn.close()

    if afectados == 0:
        raise HTTPException(status_code=404, detail="Seguimiento no encontrado")

    return {"mensaje": f"Seguimiento con ID {seguimiento_id} eliminado correctamente"}