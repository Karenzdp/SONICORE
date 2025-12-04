from sqlmodel import SQLModel, Field
from typing import Optional
from app.models.base import BaseControl

class Usuario(BaseControl, table=True): # Hereda
    __tablename__ = "usuarios"
    id_usuario: Optional[int] = Field(default=None, primary_key=True)
    nombre_usuario: str = Field(index=True, unique=True)
    correo: str = Field(unique=True)
    contrasena: str

class UsuarioCreate(SQLModel):
    nombre_usuario: str
    correo: str
    contrasena: str

class UsuarioRead(SQLModel):
    id_usuario: int
    nombre_usuario: str
    activo: bool