import re
from pydantic import BaseModel, field_validator
from typing import Optional

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"

class ConfiguredModel(BaseModel):
    class Config:
        from_attributes = True

# --- Autenticación y Usuarios ---
class Token(BaseModel):
    access_token: str
    token_type: str

class UsuarioRegistro(ConfiguredModel):
    nombre: str
    email: str
    password: str

    @field_validator('email')
    @classmethod
    def validar_email(cls, v: str) -> str:
        if not re.match(EMAIL_REGEX, v):
            raise ValueError('El correo electronico no es valido')
        return v

class UsuarioRespuesta(ConfiguredModel):
    id: int
    nombre: str
    email: str
    rol_id: Optional[int] = 2

class UsuarioLogin(BaseModel):
    email: str
    password: str

    @field_validator('email')
    @classmethod
    def validar_email(cls, v: str) -> str:
        if not re.match(EMAIL_REGEX, v):
            raise ValueError('El correo electronico no es valido')
        return v

# --- Especies ---
class EspecieCrear(ConfiguredModel):
    nombre: str
    descripcion: Optional[str] = None

class EspecieRespuesta(ConfiguredModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None

# --- Refugios ---
class RefugioCrear(ConfiguredModel):
    nombre: str
    direccion: str
    telefono: Optional[str] = None

class RefugioRespuesta(ConfiguredModel):
    id: int
    nombre: str
    direccion: str
    telefono: Optional[str] = None

# --- Animales ---
class AnimalCrear(ConfiguredModel):
    nombre: str
    edad: Optional[int] = None
    especie_id: int
    refugio_id: int
    estado: Optional[str] = "Disponible"

class AnimalRespuesta(ConfiguredModel):
    id: int
    nombre: str
    edad: Optional[int] = None
    especie_id: int
    refugio_id: int
    estado: str

# --- Historiales Médicos ---
class HistorialMedicoCrear(ConfiguredModel):
    animal_id: int
    descripcion: str
    fecha: str

class HistorialMedicoRespuesta(ConfiguredModel):
    id: int
    animal_id: int
    descripcion: str
    fecha: str

# --- Solicitudes de Adopción ---
class SolicitudAdopcionCrear(ConfiguredModel):
    animal_id: int
    fecha: str

class SolicitudActualizarEstado(ConfiguredModel):
    estado: str  # Ej: "Aprobada", "Rechazada", "En Revisión"

class SolicitudAdopcionRespuesta(ConfiguredModel):
    id: int
    animal_id: int
    usuario_id: int
    estado: str
    fecha: str

# --- Seguimientos ---
class SeguimientoCrear(ConfiguredModel):
    solicitud_id: int
    observaciones: str
    fecha: str

class SeguimientoRespuesta(ConfiguredModel):
    id: int
    solicitud_id: int
    observaciones: str
    fecha: str

# --- Alias de Compatibilidad ---
UsuarioCrear = UsuarioRegistro
HistorialCrear = HistorialMedicoCrear
HistorialRespuesta = HistorialMedicoRespuesta
SolicitudCrear = SolicitudAdopcionCrear
SolicitudRespuesta = SolicitudAdopcionRespuesta