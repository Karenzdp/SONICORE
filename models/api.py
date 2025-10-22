from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class API(SQLModel, table=True):
    __tablename__ = "apis"

    id_api: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    url_base: str
    descripcion: Optional[str] = None
    activo: bool = Field(default=True)
    fecha_registro: datetime = Field(default_factory=datetime.utcnow)

# SCHEMAS PARA API 

class APICreate(SQLModel):
    #Schema para crear una API (entrada)
    nombre: str
    url_base: str
    descripcion: Optional[str] = None
    


class APIRead(SQLModel):
    #Schema para leer una API (salida)
    id_api: int
    nombre: str
    url_base: str
    descripcion: Optional[str] = None

    #fecha_registro: datetime

class APIUpdate(SQLModel):
    nombre: Optional[str] = ""
    url_base: Optional[str] = ""
    descripcion: Optional[str] = ""
    