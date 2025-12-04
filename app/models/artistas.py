from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING, List
from datetime import date
from app.models.base import BaseControl

if TYPE_CHECKING:
    from app.models.generos import Genero
    from app.models.canciones import Cancion
    from app.models.albumes import Album


# --- CLASE BD ---
class Artista(BaseControl, table=True):
    __tablename__ = "artistas"
    id_artista: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    nacionalidad: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    biografia: Optional[str] = None
    foto: Optional[str] = None
    genero_principal_id: int = Field(foreign_key="generos.id_genero")

    genero_principal: Optional["Genero"] = Relationship(back_populates="artistas")
    canciones: List["Cancion"] = Relationship(back_populates="artista")
    albunes: List["Album"] = Relationship(back_populates="artista_principal")


# --- ESQUEMAS ---

class ArtistaCreate(SQLModel):
    nombre: str
    nacionalidad: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    biografia: Optional[str] = None
    foto: Optional[str] = None
    genero_principal_id: int


# 👇 AQUÍ ESTABA EL PROBLEMA: Faltaba 'biografia' en esta lista
class ArtistaRead(SQLModel):
    id_artista: int
    nombre: str
    nacionalidad: Optional[str] = None
    foto: Optional[str] = None
    biografia: Optional[str] = None  # <--- ¡SI ESTO NO ESTÁ, NO SE VE!
    activo: bool


class ArtistaUpdate(SQLModel):
    nombre: Optional[str] = None
    nacionalidad: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    biografia: Optional[str] = None
    foto: Optional[str] = None
    genero_principal_id: Optional[int] = None