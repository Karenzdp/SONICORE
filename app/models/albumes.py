from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from app.models.base import BaseControl

if TYPE_CHECKING:
    from app.models.artistas import Artista
    from app.models.generos import Genero
    from app.models.canciones import Cancion

# --- MODELO BD ---
class Album(BaseControl, table=True):
    __tablename__ = "albunes"
    id_album: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    anio_lanzamiento: Optional[int] = None
    foto_portada: Optional[str] = None
    descripcion: Optional[str] = None
    artista_principal_id: int = Field(foreign_key="artistas.id_artista")
    genero_id: Optional[int] = Field(default=None, foreign_key="generos.id_genero")

    artista_principal: Optional["Artista"] = Relationship(back_populates="albunes")
    genero: Optional["Genero"] = Relationship(back_populates="albunes")
    canciones: List["Cancion"] = Relationship(back_populates="album")

# --- ESQUEMAS ---
class AlbumCreate(SQLModel):
    nombre: str
    anio_lanzamiento: Optional[int] = None
    # 👇 AGREGAMOS ESTOS CAMPOS QUE FALTABAN:
    foto_portada: Optional[str] = None
    descripcion: Optional[str] = None
    artista_principal_id: int
    genero_id: int

class AlbumRead(SQLModel):
    id_album: int
    nombre: str
    anio_lanzamiento: Optional[int] = None
    foto_portada: Optional[str] = None # Para que el frontend muestre la imagen
    activo: bool

class AlbumUpdate(SQLModel):
    nombre: Optional[str] = None
    anio_lanzamiento: Optional[int] = None
    foto_portada: Optional[str] = None
    descripcion: Optional[str] = None
    artista_principal_id: Optional[int] = None
    genero_id: Optional[int] = None