import sqlite3
import hashlib
import hmac
import base64
import json
import time
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database import obtener_conexion

SECRET_KEY = "clave_secreta_sena_python_nativo"

security_scheme = HTTPBearer()

def obtener_password_hash(password: str) -> str:
    salt = "sena_salt_fixed"
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return key.hex()

def verificar_password(plain_password: str, hashed_password: str) -> bool:
    return obtener_password_hash(plain_password) == hashed_password

def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

# Función auxiliar para decodificar Base64URL sin errores de padding
def _base64url_decode(data: str) -> bytes:
    padding = '=' * (4 - (len(data) % 4))
    return base64.urlsafe_b64decode(data + padding)

def crear_token_acceso(data: dict, expires_in: int = 3600) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = data.copy()
    payload["exp"] = int(time.time()) + expires_in

    header_b64 = _base64url_encode(json.dumps(header).encode('utf-8'))
    payload_b64 = _base64url_encode(json.dumps(payload).encode('utf-8'))

    signature_input = f"{header_b64}.{payload_b64}".encode('utf-8')
    signature = hmac.new(SECRET_KEY.encode('utf-8'), signature_input, hashlib.sha256).digest()
    signature_b64 = _base64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{signature_b64}"

def obtener_usuario_actual(auth: HTTPAuthorizationCredentials = Depends(security_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas o token expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = auth.credentials

    try:
        parts = token.split('.')
        if len(parts) != 3:
            raise credentials_exception
        
        header_b64, payload_b64, signature_b64 = parts
        
        # 1. Validar la firma utilizando hmac.compare_digest para evitar ataques de tiempo
        signature_input = f"{header_b64}.{payload_b64}".encode('utf-8')
        expected_sig = _base64url_encode(hmac.new(SECRET_KEY.encode('utf-8'), signature_input, hashlib.sha256).digest())
        
        if not hmac.compare_digest(signature_b64, expected_sig):
            raise credentials_exception

        # 2. Decodificar payload usando la nueva función con padding exacto
        payload_bytes = _base64url_decode(payload_b64)
        payload = json.loads(payload_bytes.decode('utf-8'))
        
        if payload.get("exp", 0) < time.time():
            raise credentials_exception

        usuario_id = payload.get("sub")
        if not usuario_id:
            raise credentials_exception

    except Exception:
        raise credentials_exception

    conn = obtener_conexion()
    cursor = conn.cursor()
    row = cursor.execute(
        "SELECT id, nombre, email, password_hash, rol_id FROM usuarios WHERE id = ?", 
        (usuario_id,)
    ).fetchone()
    conn.close()

    if row is None:
        raise credentials_exception
        
    return dict(row)

# Asegúrate de tener también definida la función requerir_admin
def requerir_admin(usuario_actual: dict = Depends(obtener_usuario_actual)) -> dict:
    if usuario_actual.get("rol_id") != 1:  # Asumiendo que 1 es el rol de Administrador
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos suficientes para realizar esta acción"
        )
    return usuario_actual