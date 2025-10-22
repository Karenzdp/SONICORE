from datetime import date
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from models.artistas import Artista
    from models.albumes import Album
    from models.generos import Genero

class Cancion(SQLModel, table=True):
    __tablename__ = "canciones"

    id_cancion: Optional[int] = Field(default=None, primary_key=True)
    titulo: str
    duracion: Optional[str] = None  # minutos o segundos
    anio_lanzamiento: Optional[int] = None
    portada: Optional[str] = None
    activo: bool = Field(default=True)
    
    artista_id: int = Field(foreign_key="artistas.id_artista")
    album_id: Optional[int] = Field(default=None, foreign_key="albunes.id_album")
    genero_id: Optional[int] = Field(default=None, foreign_key="generos.id_genero")

    # Relaciones
    artista: Optional["Artista"] = Relationship(back_populates="canciones")
    album: Optional["Album"] = Relationship(back_populates="canciones")
    genero: Optional["Genero"] = Relationship(back_populates="canciones")


# SCHEMAS
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
    anio_lanzamiento: Optional[int] = None
    portada: Optional[str] = None
    artista_id: int
    album_id: Optional[int] = None
    genero_id: Optional[int] = None
    
class CancionUpdate(SQLModel):
    titulo: Optional[str] = ""
    duracion: Optional[str] = ""
    anio_lanzamiento: Optional[int] = None
    album_id: Optional[int] = None
    #artista_id: Optional[int] = None
