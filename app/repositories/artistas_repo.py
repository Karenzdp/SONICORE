from sqlmodel import Session, select
from fastapi import HTTPException
from app.repositories.base import BaseRepository
from app.models.artistas import Artista, ArtistaCreate
from app.models.generos import Genero

class ArtistaRepository(BaseRepository[Artista]):
    def __init__(self, session: Session):
        super().__init__(session, Artista)

    def crear_validado(self, datos: ArtistaCreate) -> Artista:
        if datos.genero_principal_id:
            if not self.session.get(Genero, datos.genero_principal_id):
                raise HTTPException(400, "Género no encontrado")

        nuevo = Artista.model_validate(datos)
        return self.create(nuevo)

    # 👇 ESTA TAMBIÉN ES NECESARIA PARA EL IMPORTADOR
    def buscar_por_nombre(self, nombre: str):
        statement = select(Artista).where(Artista.nombre.ilike(f"%{nombre}%"))
        return self.session.exec(statement).all()

    def crear_artista(self, nombre, nacionalidad, foto, biografia, genero_principal_id):
        nuevo = Artista(
            nombre=nombre,
            nacionalidad=nacionalidad,
            foto=foto,
            biografia=biografia,
            genero_principal_id=genero_principal_id
        )
        return self.create(nuevo)