from sqlmodel import SQLModel, Field
from typing import Optional

class Favorito(SQLModel, table=True):
    """
    Tabla de unión para guardar qué usuario le dio like a qué canción.
    """
    __tablename__ = "favoritos"

    # Usamos una clave primaria compuesta (un usuario no puede likear la misma canción 2 veces)
    usuario_id: int = Field(foreign_key="usuarios.id_usuario", primary_key=True)
    cancion_id: int = Field(foreign_key="canciones.id_cancion", primary_key=True)