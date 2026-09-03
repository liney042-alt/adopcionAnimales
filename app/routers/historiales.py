from fastapi import APIRouter, HTTPException, Depends, status
import sqlite3
from app.database import obtener_conexion
from app import schemas, security

router = APIRouter(prefix="/historiales", tags=["Historiales Médicos"])

@router.get("/", response_model=list[schemas.HistorialRespuesta])
def listar_historiales(usuario_actual: dict = Depends(security.obtener_usuario_actual)):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM historiales_medicos")
    historiales = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return historiales

@router.get("/{historial_id}", response_model=schemas.HistorialRespuesta)
def obtener_historial(historial_id: int, usuario_actual: dict = Depends(security.obtener_usuario_actual)):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM historiales_medicos WHERE id = ?", (historial_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Historial médico no encontrado")
    return dict(row)

@router.post("/", response_model=schemas.HistorialRespuesta, status_code=status.HTTP_201_CREATED)
def crear_historial(
    historial: schemas.HistorialCrear,
    admin: dict = Depends(security.requerir_admin)
):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO historiales_medicos (animal_id, fecha, diagnostico, tratamiento) VALUES (?, ?, ?, ?)",
        (historial.animal_id, historial.fecha, historial.diagnostico, historial.tratamiento)
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()
    return {**historial.model_dump(), "id": nuevo_id}

@router.delete("/{historial_id}", status_code=status.HTTP_200_OK)
def eliminar_historial(
    historial_id: int,
    admin: dict = Depends(security.requerir_admin)
):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM historiales_medicos WHERE id = ?", (historial_id,))
    afectados = cursor.rowcount
    conn.commit()
    conn.close()

    if afectados == 0:
        raise HTTPException(status_code=404, detail="Historial médico no encontrado")

    return {"mensaje": f"Historial médico con ID {historial_id} eliminado correctamente"}