from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Usuario(SQLModel, table=True):
    __tablename__ = "usuarios"

    id_usuario: Optional[int] = Field(default=None, primary_key=True)
    nombre_usuario: str = Field(index=True, unique=True)
    correo: str = Field(unique=True)
    contrasena: str
    activo: bool = Field(default=True)
    fecha_registro: datetime = Field(default_factory=datetime.utcnow)

# SCHEMAS
class UsuarioCreate(SQLModel):
    nombre_usuario: str
    correo: str
    contrasena: str


class UsuarioRead(SQLModel):
    id_usuario: int
    nombre_usuario: str
    correo: str
    activo: bool
    fecha_registro: datetime


class UsuarioUpdate(SQLModel):
    nombre_usuario: Optional[str] = ""
    correo: Optional[str] = ""
    contrasena: Optional[str] = ""
    activo: Optional[bool] = True





