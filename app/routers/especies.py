from fastapi import APIRouter, HTTPException, Depends, status
import sqlite3
from app.database import obtener_conexion
from app import schemas, security

router = APIRouter(prefix="/especies", tags=["Especies"])

@router.get("/", response_model=list[schemas.EspecieRespuesta])
def listar_especies():
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM especies")
    especies = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return especies

@router.get("/{especie_id}", response_model=schemas.EspecieRespuesta)
def obtener_especie(especie_id: int):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM especies WHERE id = ?", (especie_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Especie no encontrada")
    return dict(row)

@router.post("/", response_model=schemas.EspecieRespuesta, status_code=status.HTTP_201_CREATED)
def crear_especie(
    especie: schemas.EspecieCrear,
    admin: dict = Depends(security.requerir_admin)
):
    conn = obtener_conexion()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO especies (nombre) VALUES (?)", (especie.nombre,))
        conn.commit()
        nuevo_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="La especie ya se encuentra registrada")
    conn.close()
    return {**especie.model_dump(), "id": nuevo_id}

@router.delete("/{especie_id}", status_code=status.HTTP_200_OK)
def eliminar_especie(
    especie_id: int,
    admin: dict = Depends(security.requerir_admin)
):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM especies WHERE id = ?", (especie_id,))
    afectados = cursor.rowcount
    conn.commit()
    conn.close()

    if afectados == 0:
        raise HTTPException(status_code=404, detail="Especie no encontrada")

    return {"mensaje": f"Especie con ID {especie_id} eliminada correctamente"}