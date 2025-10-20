from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
if TYPE_CHECKING:
    from models.artistas import Artista

class Genero(SQLModel, table=True):
    __tablename__ = "generos"

    id_genero: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    descripcion: Optional[str] = None

    # Relación inversa (un género puede tener varios artistas)
    artistas: List["Artista"] = Relationship(back_populates="genero_principal")
    
# ========== SCHEMAS PARA API ==========

class GeneroCreate(SQLModel):
    """Schema para crear un género (entrada)"""
    nombre:str
    descripción: Optional[str]=None

class GeneroRead(SQLModel):
    id_genero: int
    nombre:str
    descripcion: Optional[str]= None