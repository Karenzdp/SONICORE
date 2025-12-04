from sqlmodel import Session
# Debes decirle a Python que busque DENTRO de la carpeta repositories
from app.repositories.base import BaseRepository
from app.models.api import API


class APIRepository(BaseRepository[API]):
    def __init__(self, session: Session):
        super().__init__(session, API)

