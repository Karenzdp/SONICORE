from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from app.models.base import BaseControl

if TYPE_CHECKING:
    from app.models.artistas import Artista
    from app.models.generos import Genero
    from app.models.canciones import Cancion
"""reistras de forma individual por p¿jugadro en cada encuentro, (o  importa si splo ingresounos minutos), estaditicas de participacion con las que 
represena el total de tiempo en la cancha en minutps, este dato ser de lto valor, entendiendo que no es lo mismo 2 goles en 90 minutos que 2 goles en 15. las est 
ofensivas son la represenacion de los goles anotados por el jgador urante su intervencion en un partido. importante tener faltas y tarjetas que recibe, , con ellas se modifica el estado del jugadr suspendido 
y a antidad de encuentros que se perdera o perdio

"""
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
