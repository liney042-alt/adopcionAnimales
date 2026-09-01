import sqlite3
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from app.database import obtener_conexion
from app import schemas, security

router = APIRouter(tags=["Autenticación y Usuarios"])

@router.post("/registro", response_model=schemas.UsuarioRespuesta, status_code=status.HTTP_201_CREATED)
def registrar_usuario(usuario: schemas.UsuarioRegistro):
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    existe = cursor.execute("SELECT id FROM usuarios WHERE email = ?", (usuario.email,)).fetchone()
    if existe:
        conn.close()
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    
    hashed_pwd = security.obtener_password_hash(usuario.password)
    cursor.execute(
        "INSERT INTO usuarios (nombre, email, password_hash, rol_id) VALUES (?, ?, ?, ?)",
        (usuario.nombre, usuario.email, hashed_pwd, usuario.rol_id)
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()
    
    return {"id": nuevo_id, "nombre": usuario.nombre, "email": usuario.email, "rol_id": usuario.rol_id}

@router.post("/token", response_model=schemas.Token)
def login_para_token(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = obtener_conexion()
    cursor = conn.cursor()
    usuario = cursor.execute("SELECT * FROM usuarios WHERE email = ?", (form_data.username,)).fetchone()
    conn.close()

    if not usuario or not security.verificar_password(form_data.password, usuario["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_acceso = security.crear_token_acceso(data={"sub": usuario["email"]})
    return {"access_token": token_acceso, "token_type": "bearer"}

@router.get("/usuarios/me", response_model=schemas.UsuarioRespuesta)
def leer_usuario_actual(usuario_actual: dict = Depends(security.obtener_usuario_actual)):
    return usuario_actual