import sqlite3
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.database import obtener_conexion
from app import schemas, security

router = APIRouter(prefix="/animales", tags=["Animales"])

@router.get("/", response_model=List[schemas.AnimalRespuesta])
def listar_animales():
    conn = obtener_conexion()
    cursor = conn.cursor()
    animales = cursor.execute("SELECT id, nombre, edad, especie_id, refugio_id, estado FROM animales").fetchall()
    conn.close()
    return [dict(a) for a in animales]

@router.get("/{animal_id}", response_model=schemas.AnimalRespuesta)
def obtener_animal(animal_id: int):
    conn = obtener_conexion()
    cursor = conn.cursor()
    animal = cursor.execute("SELECT id, nombre, edad, especie_id, refugio_id, estado FROM animales WHERE id = ?", (animal_id,)).fetchone()
    conn.close()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal no encontrado")
    return dict(animal)

@router.post("/", response_model=schemas.AnimalRespuesta, status_code=status.HTTP_201_CREATED)
def crear_animal(
    animal: schemas.AnimalCrear,
    admin_actual: dict = Depends(security.requerir_admin)
):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO animales (nombre, edad, especie_id, refugio_id, estado) VALUES (?, ?, ?, ?, ?)",
        (animal.nombre, animal.edad, animal.especie_id, animal.refugio_id, animal.estado or "Disponible")
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()
    return {"id": nuevo_id, **animal.model_dump()}

@router.put("/{animal_id}", response_model=schemas.AnimalRespuesta)
def actualizar_animal(
    animal_id: int,
    datos: schemas.AnimalCrear,
    admin_actual: dict = Depends(security.requerir_admin)
):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE animales SET nombre = ?, edad = ?, especie_id = ?, refugio_id = ?, estado = ? WHERE id = ?",
        (datos.nombre, datos.edad, datos.especie_id, datos.refugio_id, datos.estado, animal_id)
    )
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Animal no encontrado")
    conn.commit()
    conn.close()
    return {"id": animal_id, **datos.model_dump()}

@router.delete("/{animal_id}")
def eliminar_animal(
    animal_id: int,
    admin_actual: dict = Depends(security.requerir_admin)
):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute("DELETE FROM animales WHERE id = ?", (animal_id,))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Animal no encontrado")
    conn.commit()
    conn.close()
    return {"mensaje": f"Animal {animal_id} eliminado exitosamente (sus historiales y solicitudes asociadas se eliminaron en cascada)"}

# Eliminar animal (Exclusivo para Administradores)
@router.delete("/{animal_id}", status_code=status.HTTP_200_OK)
def eliminar_animal(
    animal_id: int,
    admin_actual: dict = Depends(security.requerir_admin) # Protege el endpoint solo para ROL Admin (rol_id = 1)
):
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM animales WHERE id = ?", (animal_id,))
    afectados = cursor.rowcount
    conn.commit()
    conn.close()

    if afectados == 0:
        raise HTTPException(status_code=404, detail="Animal no encontrado")
        
    return {"mensaje": f"Animal con ID {animal_id} eliminado correctamente"}