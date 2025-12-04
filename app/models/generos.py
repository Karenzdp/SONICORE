from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from app.models.base import BaseControl

if TYPE_CHECKING:
    from app.models.artistas import Artista
    from app.models.canciones import Cancion
    from app.models.albumes import Album


class Genero(BaseControl, table=True):  # Hereda
    __tablename__ = "generos"
    id_genero: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    descripcion: Optional[str] = None

    artistas: List["Artista"] = Relationship(back_populates="genero_principal")
    canciones: List["Cancion"] = Relationship(back_populates="genero")
    albunes: List["Album"] = Relationship(back_populates="genero")


class GeneroCreate(SQLModel):
    nombre: str
    descripcion: Optional[str] = None


class GeneroRead(SQLModel):
    id_genero: int
    nombre: str
    descripcion: Optional[str] = None
    activo: bool


class GeneroUpdate(SQLModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None