import sqlite3
import hashlib
import hmac
import base64
import json
import time
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials # <--- Importar HTTPBearer
from app.database import obtener_conexion

SECRET_KEY = "clave_secreta_sena_python_nativo"

# Reemplazamos OAuth2PasswordBearer por HTTPBearer
security_scheme = HTTPBearer()

def obtener_password_hash(password: str) -> str:
    salt = "sena_salt_fixed"
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return key.hex()

def verificar_password(plain_password: str, hashed_password: str) -> bool:
    return obtener_password_hash(plain_password) == hashed_password

def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

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

# Actualizamos la extracción del token recibido desde HTTPBearer
def obtener_usuario_actual(auth: HTTPAuthorizationCredentials = Depends(security_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas o token expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = auth.credentials  # extrae directamente el token pasado en el header Authorization

    try:
        parts = token.split('.')
        if len(parts) != 3:
            raise credentials_exception
        
        header_b64, payload_b64, signature_b64 = parts
        signature_input = f"{header_b64}.{payload_b64}".encode('utf-8')
        expected_sig = _base64url_encode(hmac.new(SECRET_KEY.encode('utf-8'), signature_input, hashlib.sha256).digest())
        
        if signature_b64 != expected_sig:
            raise credentials_exception

        payload = json.loads(base64.urlsafe_b64decode(payload_b64 + '==='))
        if payload.get("exp", 0) < time.time():
            raise credentials_exception

        email: str = payload.get("sub")
        if not email:
            raise credentials_exception

    except Exception:
        raise credentials_exception

    conn = obtener_conexion()
    cursor = conn.cursor()
    row = cursor.execute("SELECT id, nombre, email, password_hash, rol_id FROM usuarios WHERE email = ?", (email,)).fetchone()
    conn.close()

    if row is None:
        raise credentials_exception
    return dict(row)

def requerir_admin(usuario_actual: dict = Depends(obtener_usuario_actual)) -> dict:
    if usuario_actual["rol_id"] != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de Administrador"
        )
    return usuario_actual