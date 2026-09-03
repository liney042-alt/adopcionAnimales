import sqlite3
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.database import obtener_conexion
from app import schemas, security

router = APIRouter(prefix="/refugios", tags=["Refugios"])

@router.get("/", response_model=List[schemas.RefugioRespuesta])
def listar_refugios():
    conn = obtener_conexion()
    cursor = conn.cursor()
    refugios = cursor.execute("SELECT id, nombre, direccion, telefono FROM refugios").fetchall()
    conn.close()
    return [dict(r) for r in refugios]

@router.get("/{refugio_id}", response_model=schemas.RefugioRespuesta)
def obtener_refugio(refugio_id: int):
    conn = obtener_conexion()
    cursor = conn.cursor()
    refugio = cursor.execute("SELECT id, nombre, direccion, telefono FROM refugios WHERE id = ?", (refugio_id,)).fetchone()
    conn.close()
    if not refugio:
        raise HTTPException(status_code=404, detail="Refugio no encontrado")
    return dict(refugio)

@router.post("/", response_model=schemas.RefugioRespuesta, status_code=status.HTTP_201_CREATED)
def crear_refugio(
    refugio: schemas.RefugioCrear,
    admin_actual: dict = Depends(security.requerir_admin)
):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO refugios (nombre, direccion, telefono) VALUES (?, ?, ?)",
        (refugio.nombre, refugio.direccion, refugio.telefono)
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()
    return {"id": nuevo_id, **refugio.model_dump()}

@router.put("/{refugio_id}", response_model=schemas.RefugioRespuesta)
def actualizar_refugio(
    refugio_id: int,
    datos: schemas.RefugioCrear,
    admin_actual: dict = Depends(security.requerir_admin)
):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE refugios SET nombre = ?, direccion = ?, telefono = ? WHERE id = ?",
        (datos.nombre, datos.direccion, datos.telefono, refugio_id)
    )
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Refugio no encontrado")
    conn.commit()
    conn.close()
    return {"id": refugio_id, **datos.model_dump()}

# Eliminar refugio (Exclusivo Administrador)
@router.delete("/{refugio_id}", status_code=status.HTTP_200_OK)
def eliminar_refugio(
    refugio_id: int,
    admin: dict = Depends(security.requerir_admin)
):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM refugios WHERE id = ?", (refugio_id,))
    afectados = cursor.rowcount
    conn.commit()
    conn.close()

    if afectados == 0:
        raise HTTPException(status_code=404, detail="Refugio no encontrado")

    return {"mensaje": f"Refugio con ID {refugio_id} eliminado correctamente"}