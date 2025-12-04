from sqlmodel import SQLModel, Field
from datetime import datetime

class BaseControl(SQLModel):
    """Clase Padre: Todos los modelos tendrán esto automáticamente."""
    activo: bool = Field(default=True)
    fecha_registro: datetime = Field(default_factory=datetime.utcnow)