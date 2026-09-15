import sqlite3
from fastapi import APIRouter, HTTPException, Depends, status
from app.database import obtener_conexion
from app import schemas, security

router = APIRouter(prefix="/solicitudes", tags=["Solicitudes de Adopción"])

@router.get("/", response_model=list[schemas.SolicitudRespuesta])
def listar_solicitudes(usuario_actual: dict = Depends(security.obtener_usuario_actual)):
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    # Admin (rol_id = 1) ve todas; Usuario común (rol_id = 2) solo ve las suyas
    if usuario_actual.get("rol_id") == 1:
        cursor.execute("SELECT * FROM solicitudes_adopcion")
    else:
        cursor.execute("SELECT * FROM solicitudes_adopcion WHERE usuario_id = ?", (usuario_actual["id"],))
    
    solicitudes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return solicitudes

@router.get("/{solicitud_id}", response_model=schemas.SolicitudRespuesta)
def obtener_solicitud(
    solicitud_id: int, 
    usuario_actual: dict = Depends(security.obtener_usuario_actual)
):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM solicitudes_adopcion WHERE id = ?", (solicitud_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    
    solicitud = dict(row)
    
    # Restricción: un usuario normal no puede consultar la solicitud de otro
    if usuario_actual.get("rol_id") != 1 and solicitud["usuario_id"] != usuario_actual["id"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver esta solicitud")
        
    return solicitud

@router.post("/", response_model=schemas.SolicitudRespuesta, status_code=status.HTTP_201_CREATED)
def crear_solicitud(
    solicitud: schemas.SolicitudCrear,
    usuario_actual: dict = Depends(security.obtener_usuario_actual)
):
    conn = obtener_conexion()
    cursor = conn.cursor()
    usuario_id = usuario_actual["id"]
    estado_inicial = "Pendiente"
    
    # 1. Validar que el animal exista y esté disponible
    cursor.execute("SELECT estado FROM animales WHERE id = ?", (solicitud.animal_id,))
    animal = cursor.fetchone()
    
    if not animal:
        conn.close()
        raise HTTPException(status_code=404, detail="El animal especificado no existe")
        
    if animal["estado"] == "Adoptado":
        conn.close()
        raise HTTPException(status_code=400, detail="Este animal ya ha sido adoptado")
    
    # 2. Registrar la solicitud
    try:
        cursor.execute(
            "INSERT INTO solicitudes_adopcion (usuario_id, animal_id, estado, fecha) VALUES (?, ?, ?, ?)",
            (usuario_id, solicitud.animal_id, estado_inicial, solicitud.fecha)
        )
        conn.commit()
        nuevo_id = cursor.lastrowid
    except sqlite3.IntegrityError as e:
        conn.close()
        error_msg = str(e).lower()
        if "foreign key" in error_msg:
            raise HTTPException(status_code=400, detail="El animal o usuario especificado no existe")
        raise HTTPException(status_code=400, detail="Error de integridad al registrar la solicitud")
        
    conn.close()
    return {
        "id": nuevo_id,
        "usuario_id": usuario_id,
        "animal_id": solicitud.animal_id,
        "estado": estado_inicial,
        "fecha": solicitud.fecha
    }

@router.put("/{solicitud_id}", response_model=schemas.SolicitudRespuesta)
def actualizar_estado_solicitud(
    solicitud_id: int,
    datos: schemas.SolicitudActualizarEstado,
    admin: dict = Depends(security.requerir_admin)
):
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    # 1. Verificar existencia de la solicitud y obtener el id del animal
    cursor.execute("SELECT animal_id FROM solicitudes_adopcion WHERE id = ?", (solicitud_id,))
    solicitud = cursor.fetchone()
    if not solicitud:
        conn.close()
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
        
    animal_id = solicitud["animal_id"]
    
    # 2. Actualizar el estado de la solicitud
    cursor.execute(
        "UPDATE solicitudes_adopcion SET estado = ? WHERE id = ?",
        (datos.estado, solicitud_id)
    )
    
    # 3. Sincronizar estado del animal
    if datos.estado == "Aprobada":
        cursor.execute("UPDATE animales SET estado = 'Adoptado' WHERE id = ?", (animal_id,))
    elif datos.estado in ["Rechazada", "Cancelada"]:
        cursor.execute("UPDATE animales SET estado = 'Disponible' WHERE id = ?", (animal_id,))
        
    conn.commit()
    
    # 4. Retornar el registro actualizado
    cursor.execute("SELECT * FROM solicitudes_adopcion WHERE id = ?", (solicitud_id,))
    solicitud_actualizada = cursor.fetchone()
    conn.close()
    
    return dict(solicitud_actualizada)

@router.delete("/{solicitud_id}", status_code=status.HTTP_200_OK)
def eliminar_solicitud(
    solicitud_id: int,
    usuario_actual: dict = Depends(security.obtener_usuario_actual)
):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT usuario_id, estado, animal_id FROM solicitudes_adopcion WHERE id = ?", (solicitud_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
        
    solicitud = dict(row)
    
    es_admin = usuario_actual.get("rol_id") == 1
    es_dueno = solicitud["usuario_id"] == usuario_actual["id"]
    
    if not es_admin:
        if not es_dueno:
            conn.close()
            raise HTTPException(status_code=403, detail="No tienes permiso para cancelar esta solicitud")
        if solicitud["estado"] != "Pendiente":
            conn.close()
            raise HTTPException(status_code=400, detail="Solo puedes cancelar solicitudes en estado Pendiente")
            
    # Liberar el animal si la solicitud que se elimina estaba Aprobada
    if solicitud["estado"] == "Aprobada":
        cursor.execute("UPDATE animales SET estado = 'Disponible' WHERE id = ?", (solicitud["animal_id"],))

    cursor.execute("DELETE FROM solicitudes_adopcion WHERE id = ?", (solicitud_id,))
    conn.commit()
    conn.close()

    return {"mensaje": f"Solicitud con ID {solicitud_id} cancelada/eliminada correctamente"}