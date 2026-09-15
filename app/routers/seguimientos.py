import sqlite3
from fastapi import APIRouter, HTTPException, Depends, status
from app.database import obtener_conexion
from app import schemas, security

router = APIRouter(prefix="/seguimientos", tags=["Seguimientos"])

@router.get("/", response_model=list[schemas.SeguimientoRespuesta])
def listar_seguimientos(usuario_actual: dict = Depends(security.obtener_usuario_actual)):
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    # Administrador ve todo; usuario normal solo ve seguimientos de sus solicitudes
    if usuario_actual.get("rol_id") == 1:
        cursor.execute("SELECT * FROM seguimientos")
    else:
        cursor.execute("""
            SELECT s.* FROM seguimientos s
            JOIN solicitudes_adopcion sol ON s.solicitud_id = sol.id
            WHERE sol.usuario_id = ?
        """, (usuario_actual["id"],))
        
    seguimientos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return seguimientos

@router.get("/{seguimiento_id}", response_model=schemas.SeguimientoRespuesta)
def obtener_seguimiento(
    seguimiento_id: int, 
    usuario_actual: dict = Depends(security.obtener_usuario_actual)
):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.*, sol.usuario_id 
        FROM seguimientos s
        JOIN solicitudes_adopcion sol ON s.solicitud_id = sol.id
        WHERE s.id = ?
    """, (seguimiento_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Seguimiento no encontrado")
        
    seguimiento = dict(row)
    
    # Verificar propiedad si no es admin
    if usuario_actual.get("rol_id") != 1 and seguimiento["usuario_id"] != usuario_actual["id"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver este seguimiento")
        
    return seguimiento

@router.post("/", response_model=schemas.SeguimientoRespuesta, status_code=status.HTTP_201_CREATED)
def crear_seguimiento(
    seguimiento: schemas.SeguimientoCrear,
    admin: dict = Depends(security.requerir_admin)
):
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO seguimientos (solicitud_id, observaciones, fecha) VALUES (?, ?, ?)",
            (seguimiento.solicitud_id, seguimiento.observaciones, seguimiento.fecha)
        )
        conn.commit()
        nuevo_id = cursor.lastrowid
    except sqlite3.IntegrityError as e:
        conn.close()
        error_msg = str(e).lower()
        if "foreign key" in error_msg:
            raise HTTPException(
                status_code=400, 
                detail="La solicitud especificada (solicitud_id) no existe"
            )
        raise HTTPException(status_code=400, detail="Error de integridad al registrar el seguimiento")

    conn.close()
    return {
        "id": nuevo_id,
        "solicitud_id": seguimiento.solicitud_id,
        "observaciones": seguimiento.observaciones,
        "fecha": seguimiento.fecha
    }

@router.put("/{seguimiento_id}", response_model=schemas.SeguimientoRespuesta)
def actualizar_seguimiento(
    seguimiento_id: int,
    datos: schemas.SeguimientoCrear,
    admin: dict = Depends(security.requerir_admin)
):
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "UPDATE seguimientos SET solicitud_id = ?, observaciones = ?, fecha = ? WHERE id = ?",
            (datos.solicitud_id, datos.observaciones, datos.fecha, seguimiento_id)
        )
        if cursor.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail="Seguimiento no encontrado")
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.close()
        error_msg = str(e).lower()
        if "foreign key" in error_msg:
            raise HTTPException(
                status_code=400, 
                detail="La solicitud especificada (solicitud_id) no existe"
            )
        raise HTTPException(status_code=400, detail="Error de integridad al actualizar el seguimiento")

    conn.close()
    return {"id": seguimiento_id, **datos.model_dump()}

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