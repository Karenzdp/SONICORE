from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from app.models.base import BaseControl

if TYPE_CHECKING:
    from app.models.artistas import Artista
    from app.models.albumes import Album
    from app.models.generos import Genero


# --- MODELO DE BASE DE DATOS ---
class Cancion(BaseControl, table=True):
    __tablename__ = "canciones"

    id_cancion: Optional[int] = Field(default=None, primary_key=True)
    titulo: str
    duracion: Optional[str] = None
    anio_lanzamiento: Optional[int] = None  # Agregado por si acaso
    portada: Optional[str] = None  # Agregado por si acaso

    # 🔑 LLAVES FORÁNEAS (Esto era lo que faltaba para que no de error)
    artista_id: int = Field(foreign_key="artistas.id_artista")
    album_id: Optional[int] = Field(default=None, foreign_key="albunes.id_album")
    genero_id: Optional[int] = Field(default=None, foreign_key="generos.id_genero")

    # 🔗 RELACIONES (Conectores)
    artista: Optional["Artista"] = Relationship(back_populates="canciones")
    album: Optional["Album"] = Relationship(back_populates="canciones")
    genero: Optional["Genero"] = Relationship(back_populates="canciones")


# --- ESQUEMAS (SCHEMAS) ---
class CancionCreate(SQLModel):
    titulo: str
    duracion: Optional[str] = None
    anio_lanzamiento: Optional[int] = None
    portada: Optional[str] = None
    artista_id: int
    album_id: Optional[int] = None
    genero_id: Optional[int] = None


class CancionRead(SQLModel):
    id_cancion: int
    titulo: str
    duracion: Optional[str] = None
    activo: bool


class CancionUpdate(SQLModel):
    titulo: Optional[str] = None
    duracion: Optional[str] = None
    artista_id: Optional[int] = None
    album_id: Optional[int] = None
    genero_id: Optional[int] = None