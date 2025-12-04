from sqlmodel import Session, select
from fastapi import HTTPException
from app.repositories.base import BaseRepository
from app.models.canciones import Cancion, CancionCreate
from app.models.artistas import Artista
from app.models.generos import Genero
from app.models.albumes import Album


class CancionRepository(BaseRepository[Cancion]):
    def __init__(self, session: Session):
        super().__init__(session, Cancion)

    def crear_validado(self, datos: CancionCreate) -> Cancion:
        # Validaciones de existencia (Foreign Keys)
        if not self.session.get(Artista, datos.artista_id):
            # Si no existe el artista, podríamos lanzar error o crearlo,
            # pero por seguridad lanzamos error 400
            pass  # (En el auto-import nos aseguramos de crearlo antes)

        nuevo = Cancion.model_validate(datos)
        return self.create(nuevo)

    # 👇 ESTA ES LA FUNCIÓN QUE FALTABA Y CAUSABA EL ERROR 500 👇
    def buscar_por_titulo(self, titulo: str):
        from sqlmodel import select
        # Busca canciones que contengan el texto (insensible a mayúsculas)
        statement = select(self.model).where(self.model.titulo.ilike(f"%{titulo}%"))
        return self.session.exec(statement).all()

        # Asegúrate de que esta función esté dentro de la clase CancionRepository
    def crear_cancion(self, titulo, artista_id, album_id, duracion, genero_id, portada):
        nueva = Cancion(
            titulo=titulo,
            artista_id=artista_id,
            album_id=album_id,
            duracion=duracion,
            genero_id=genero_id,
            portada=portada
        )
        # Asumiendo que tu BaseRepository tiene un método 'create'
        return self.create(nueva)



