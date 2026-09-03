from fastapi import APIRouter, HTTPException, Depends, status
import sqlite3
from app.database import obtener_conexion, obtener_password_hash_nativo
from app import schemas, security

router = APIRouter(prefix="", tags=["Autenticación y Usuarios"])

@router.post("/registro", response_model=schemas.UsuarioRespuesta, status_code=status.HTTP_201_CREATED)
def registrar_usuario(usuario: schemas.UsuarioRegistro):
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    hash_pass = obtener_password_hash_nativo(usuario.password)
    
    try:
        cursor.execute(
            "INSERT INTO usuarios (nombre, email, password_hash, rol_id) VALUES (?, ?, ?, ?)",
            (usuario.nombre, usuario.email, hash_pass, usuario.rol_id)
        )
        conn.commit()
        nuevo_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="El email ya se encuentra registrado")
    
    conn.close()
    return {"id": nuevo_id, "nombre": usuario.nombre, "email": usuario.email, "rol_id": usuario.rol_id}

@router.post("/token")
def login_para_token(credenciales: schemas.UsuarioLogin):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = ?", (credenciales.email,))
    row = cursor.fetchone()
    conn.close()
    
    if not row or obtener_password_hash_nativo(credenciales.password) != row["password_hash"]:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    token = security.crear_token_acceso({"sub": str(row["id"]), "rol_id": row["rol_id"], "email": row["email"]})
    return {"access_token": token, "token_type": "bearer"}

# 1. MOSTRAR USUARIO ACTUAL (Accesible para cualquier usuario autenticado)
@router.get("/usuarios/me", response_model=schemas.UsuarioRespuesta)
def leer_usuario_actual(usuario_actual: dict = Depends(security.obtener_usuario_actual)):
    return {
        "id": usuario_actual["id"],
        "email": usuario_actual.get("email", ""),
        "nombre": usuario_actual.get("nombre", "Usuario Autenticado"),
        "rol_id": usuario_actual["rol_id"]
    }

# Solo Admin puede listar todos los usuarios
@router.get("/usuarios", response_model=list[schemas.UsuarioRespuesta])
def listar_usuarios(admin: dict = Depends(security.requerir_admin)):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, email, rol_id FROM usuarios")
    usuarios = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return usuarios

# 2. SOLO ADMIN PUEDE ELIMINAR USUARIOS (Protegido por requerir_admin)
@router.delete("/usuarios/{usuario_id}", status_code=status.HTTP_200_OK)
def eliminar_usuario(
    usuario_id: int,
    admin: dict = Depends(security.requerir_admin)
):
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
        afectados = cursor.rowcount
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(
            status_code=400, 
            detail="No se puede eliminar el usuario porque tiene registros asociados"
        )
    finally:
        conn.close()

    if afectados == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return {"mensaje": f"Usuario con ID {usuario_id} eliminado correctamente"}