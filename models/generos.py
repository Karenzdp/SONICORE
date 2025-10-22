from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from models.artistas import Artista
    from models.canciones import Cancion
    from models.albumes import Album

class Genero(SQLModel, table=True):
    __tablename__ = "generos"

    id_genero: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    descripcion: Optional[str] = None
    activo: bool = Field(default=True)
    # Relaciones inversas
    artistas: List["Artista"] = Relationship(back_populates="genero_principal")
    canciones: List["Cancion"] = Relationship(back_populates="genero")
    albunes: List["Album"] = Relationship(back_populates="genero")


# SCHEMAS 
class GeneroCreate(SQLModel):
    nombre: str
    descripcion: Optional[str] = None


class GeneroRead(SQLModel):
    id_genero: int
    nombre: str
    descripcion: Optional[str] = None

class GeneroUpdate(SQLModel):
    nombre: Optional[str] = ""
    descripcion: Optional[str] = ""