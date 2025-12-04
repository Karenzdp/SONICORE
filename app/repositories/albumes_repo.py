from sqlmodel import Session
from fastapi import HTTPException
from app.repositories.base import BaseRepository
from app.models.albumes import Album, AlbumCreate
from app.models.artistas import Artista
from app.models.generos import Genero
from sqlmodel import select


class AlbumRepository(BaseRepository[Album]):
    def __init__(self, session: Session):
        super().__init__(session, Album)

    def crear_validado(self, datos: AlbumCreate) -> Album:
        # Validaciones encapsuladas
        if not self.session.get(Artista, datos.artista_principal_id):
            raise HTTPException(400, "Artista no encontrado")
        if not self.session.get(Genero, datos.genero_id):
            raise HTTPException(400, "Género no encontrado")

        nuevo = Album.model_validate(datos)
        return self.create(nuevo)

    # ... (código anterior)

    # 👇 AGREGA ESTO AL FINAL DE LA CLASE
    def buscar_por_nombre(self, nombre: str):
        statement = select(self.model).where(self.model.nombre.ilike(f"%{nombre}%"))
        return self.session.exec(statement).all()

    def crear_album(self, titulo, artista_id, anio, cover, genero_id):
        # Nota: usas 'foto_portada' en tu modelo, no 'cover', así que lo mapeamos aquí
        nuevo = Album(
            nombre=titulo,
            artista_principal_id=artista_id,
            anio_lanzamiento=anio,
            foto_portada=cover,
            genero_id=genero_id
        )
        return self.create(nuevo)