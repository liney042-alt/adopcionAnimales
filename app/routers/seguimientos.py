import sqlite3
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.database import obtener_conexion
from app import schemas, security

router = APIRouter(prefix="/seguimientos", tags=["Seguimientos Post-Adopcion"])

@router.get("/", response_model=List[schemas.SeguimientoRespuesta])
def listar_seguimientos():
    conn = obtener_conexion()
    cursor = conn.cursor()
    filas = cursor.execute("SELECT id, solicitud_id, observaciones, fecha FROM seguimientos").fetchall()
    conn.close()
    return [dict(f) for f in filas]

@router.get("/{seguimiento_id}", response_model=schemas.SeguimientoRespuesta)
def obtener_seguimiento(seguimiento_id: int):
    conn = obtener_conexion()
    cursor = conn.cursor()
    fila = cursor.execute("SELECT id, solicitud_id, observaciones, fecha FROM seguimientos WHERE id = ?", (seguimiento_id,)).fetchone()
    conn.close()
    if not fila:
        raise HTTPException(status_code=404, detail="Registro de seguimiento no encontrado")
    return dict(fila)

@router.post("/", response_model=schemas.SeguimientoRespuesta, status_code=status.HTTP_201_CREATED)
def crear_seguimiento(
    datos: schemas.SeguimientoCrear,
    usuario_actual: dict = Depends(security.obtener_usuario_actual)
):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO seguimientos (solicitud_id, observaciones, fecha) VALUES (?, ?, ?)",
        (datos.solicitud_id, datos.observaciones, str(datos.fecha))
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()
    return {"id": nuevo_id, **datos.model_dump()}