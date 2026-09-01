import sqlite3
from fastapi import APIRouter, HTTPException, status
from typing import List
from app.database import obtener_conexion
from app import schemas

router = APIRouter(prefix="/especies", tags=["Especies"])

@router.get("/", response_model=List[schemas.EspecieRespuesta])
def listar_especies():
    conn = obtener_conexion()
    cursor = conn.cursor()
    especies = cursor.execute("SELECT id, nombre, descripcion FROM especies").fetchall()
    conn.close()
    return [dict(especie) for especie in especies]

@router.get("/{especie_id}", response_model=schemas.EspecieRespuesta)
def obtener_especie(especie_id: int):
    conn = obtener_conexion()
    cursor = conn.cursor()
    especie = cursor.execute("SELECT id, nombre, descripcion FROM especies WHERE id = ?", (especie_id,)).fetchone()
    conn.close()
    
    if not especie:
        raise HTTPException(status_code=404, detail="Especie no encontrada")
    return dict(especie)

@router.post("/", response_model=schemas.EspecieRespuesta, status_code=status.HTTP_201_CREATED)
def crear_especie(especie: schemas.EspecieCrear):
    conn = obtener_conexion()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO especies (nombre, descripcion) VALUES (?, ?)",
            (especie.nombre, especie.descripcion)
        )
        conn.commit()
        nuevo_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="La especie ya existe")
    
    conn.close()
    return {"id": nuevo_id, **especie.model_dump()}

@router.delete("/{especie_id}")
def eliminar_especie(especie_id: int):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM especies WHERE id = ?", (especie_id,))
    filas_afectadas = cursor.rowcount
    conn.commit()
    conn.close()
    
    if filas_afectadas == 0:
        raise HTTPException(status_code=404, detail="Especie no encontrada")
    return {"mensaje": f"Especie {especie_id} eliminada correctamente"}