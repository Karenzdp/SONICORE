from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import date

if TYPE_CHECKING:
    from models.generos import Genero

# ========== MODELO DE BASE DE DATOS ==========
class Artista(SQLModel, table=True):
    __tablename__ = "artistas"

    id_artista: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    nacionalidad: Optional[str] = None
    fecha_nacimiento: Optional[date] = None  # date object para DB
    biografia: Optional[str] = None
    foto: Optional[str] = None

    genero_principal_id: int = Field(foreign_key="generos.id_genero")
    genero_principal: Optional["Genero"] = Relationship(back_populates="artistas")


# ========== SCHEMAS PARA API ==========
class ArtistaCreate(SQLModel):
    """Schema para crear un artista (entrada)"""
    nombre: str
    nacionalidad: Optional[str] = None
    fecha_nacimiento: Optional[date] = None  # Pydantic convierte automáticamente
    biografia: Optional[str] = None
    foto: Optional[str] = None
    genero_principal_id: Optional[int] = None


class ArtistaRead(SQLModel):
    """Schema para leer un artista (salida)"""
    id_artista: int
    nombre: str
    nacionalidad: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    biografia: Optional[str] = None
    foto: Optional[str] = None
    genero_principal_id: Optional[int] = None