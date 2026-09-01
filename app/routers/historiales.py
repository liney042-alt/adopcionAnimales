import sqlite3
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.database import obtener_conexion
from app import schemas, security

router = APIRouter(prefix="/historiales", tags=["Historiales Médicos"])

@router.get("/", response_model=List[schemas.HistorialMedicoRespuesta])
def listar_historiales():
    conn = obtener_conexion()
    cursor = conn.cursor()
    historiales = cursor.execute("SELECT id, animal_id, descripcion, fecha FROM historiales_medicos").fetchall()
    conn.close()
    return [dict(h) for h in historiales]

@router.post("/", response_model=schemas.HistorialMedicoRespuesta, status_code=status.HTTP_201_CREATED)
def crear_historial(
    historial: schemas.HistorialMedicoCrear,
    usuario_actual: dict = Depends(security.obtener_usuario_actual)
):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO historiales_medicos (animal_id, descripcion, fecha) VALUES (?, ?, ?)",
        (historial.animal_id, historial.descripcion, str(historial.fecha))
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()
    return {"id": nuevo_id, **historial.model_dump()}