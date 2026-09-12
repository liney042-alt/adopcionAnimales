import re
from pydantic import BaseModel, field_validator
from typing import Optional

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"

class Token(BaseModel):
    access_token: str
    token_type: str

class UsuarioRegistro(BaseModel):
    nombre: str
    email: str
    password: str
    rol_id: int

    @field_validator('email')
    @classmethod
    def validar_email(cls, v: str) -> str:
        if not re.match(EMAIL_REGEX, v):
            raise ValueError('El correo electronico no es valido')
        return v

class UsuarioRespuesta(BaseModel):
    id: int
    nombre: str
    email: str
    rol_id: int

class EspecieCrear(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class EspecieRespuesta(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None

class RefugioCrear(BaseModel):
    nombre: str
    direccion: str
    telefono: Optional[str] = None

class RefugioRespuesta(BaseModel):
    id: int
    nombre: str
    direccion: str
    telefono: Optional[str] = None

class AnimalCrear(BaseModel):
    nombre: str
    edad: Optional[int] = None
    especie_id: int
    refugio_id: int
    estado: Optional[str] = "Disponible"

class AnimalRespuesta(BaseModel):
    id: int
    nombre: str
    edad: Optional[int] = None
    especie_id: int
    refugio_id: int
    estado: str

class HistorialMedicoCrear(BaseModel):
    animal_id: int
    descripcion: str
    fecha: str

class HistorialMedicoRespuesta(BaseModel):
    id: int
    animal_id: int
    descripcion: str
    fecha: str

class SolicitudAdopcionCrear(BaseModel):
    animal_id: int
    fecha: str

class SolicitudAdopcionRespuesta(BaseModel):
    id: int
    animal_id: int
    usuario_id: int
    estado: str
    fecha: str

class SeguimientoCrear(BaseModel):
    solicitud_id: int
    observaciones: str
    fecha: str

class SeguimientoRespuesta(BaseModel):
    id: int
    solicitud_id: int
    observaciones: str
    fecha: str

class UsuarioLogin(BaseModel):
    email: str
    password: str

    @field_validator('email')
    @classmethod
    def validar_email(cls, v: str) -> str:
        if not re.match(EMAIL_REGEX, v):
            raise ValueError('El correo electronico no es valido')
        return v

# Alias de compatibilidad
UsuarioCrear = UsuarioRegistro

# Alias de compatibilidad para historiales y solicitudes
HistorialCrear = HistorialMedicoCrear
HistorialRespuesta = HistorialMedicoRespuesta

SolicitudCrear = SolicitudAdopcionCrear
SolicitudRespuesta = SolicitudAdopcionRespuesta