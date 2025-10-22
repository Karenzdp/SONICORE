from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING, List
from datetime import date

if TYPE_CHECKING:
    from models.generos import Genero
    from models.canciones import Cancion
    from models.albumes import Album

class Artista(SQLModel, table=True):
    __tablename__ = "artistas"

    id_artista: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    nacionalidad: Optional[str] = None
    activo: bool = Field(default=True)
    fecha_nacimiento: Optional[date] = None
    biografia: Optional[str] = None
    foto: Optional[str] = None

    genero_principal_id: int = Field(foreign_key="generos.id_genero")
    genero_principal: Optional["Genero"] = Relationship(back_populates="artistas")

    canciones: List["Cancion"] = Relationship(back_populates="artista")
    albunes: List["Album"] = Relationship(back_populates="artista_principal")


#SCHEMAS
class ArtistaCreate(SQLModel):
    nombre: str
    nacionalidad: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    biografia: Optional[str] = None
    foto: Optional[str] = None
    genero_principal_id: Optional[int] = None


class ArtistaRead(SQLModel):
    id_artista: int
    nombre: str
    nacionalidad: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    biografia: Optional[str] = None
    foto: Optional[str] = None
    genero_principal_id: Optional[int] = None
    
class ArtistaUpdate(SQLModel):
    nombre: Optional[str] = ""
    nacionalidad: Optional[str] = ""
    fecha_nacimiento: Optional[date] = None
    biografia: Optional[str] = ""
    foto: Optional[str] = ""
    #genero_principal_id: Optional[int] = None
    

