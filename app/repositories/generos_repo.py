from sqlmodel import Session, select
from app.repositories.base import BaseRepository
from app.models.generos import Genero


class GeneroRepository(BaseRepository[Genero]):
    def __init__(self, session: Session):
        super().__init__(session, Genero)

    # 👇 ESTA ES LA FUNCIÓN QUE FALTABA Y CAUSABA EL ERROR
    def buscar_por_nombre(self, nombre: str):
        # Busca géneros que coincidan con el nombre (ignorando mayúsculas/minúsculas)
        statement = select(Genero).where(Genero.nombre.ilike(f"%{nombre}%"))
        return self.session.exec(statement).all()