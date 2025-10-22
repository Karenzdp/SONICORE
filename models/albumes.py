from datetime import date
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from models.artistas import Artista
    from models.generos import Genero
    from models.canciones import Cancion

class Album(SQLModel, table=True):
    __tablename__ = "albunes"

    id_album: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    anio_lanzamiento: Optional[int] = None
    foto_portada: Optional[str] = None
    activo: bool = Field(default=True)
    descripcion: Optional[str] = None

    artista_principal_id: int = Field(foreign_key="artistas.id_artista")
    genero_id: Optional[int] = Field(default=None, foreign_key="generos.id_genero")

    artista_principal: Optional["Artista"] = Relationship(back_populates="albunes")
    genero: Optional["Genero"] = Relationship(back_populates="albunes")
    canciones: List["Cancion"] = Relationship(back_populates="album")


#SCHEMAS
class AlbumCreate(SQLModel):
    nombre: str
    anio_lanzamiento: Optional[int] = None
    foto_portada: Optional[str] = None
    descripcion: Optional[str] = None
    artista_principal_id: int
    genero_id: Optional[int] = None


class AlbumRead(SQLModel):
    id_album: int
    nombre: str
    anio_lanzamiento: Optional[int] = None
    foto_portada: Optional[str] = None
    descripcion: Optional[str] = None
    artista_principal_id: int
    genero_id: Optional[int] = None

class AlbumUpdate(SQLModel):
    nombre: Optional[str] = ""
    anio_lanzamiento: Optional[int] = None
    foto_portada: Optional[str] = ""
    descripcion: Optional[str] = ""
    artista_principal_id: Optional[int] = None
    genero_id: Optional[int] = None