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






