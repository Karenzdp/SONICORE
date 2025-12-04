from sqlmodel import Session, select
from app.models.favoritos import Favorito

class FavoritosRepository:
    def __init__(self, session: Session):
        self.session = session

    def toggle(self, usuario_id: int, cancion_id: int) -> bool:
        """
        Si existe el like, lo borra. Si no existe, lo crea.
        Retorna: True si quedó con Like, False si se quitó.
        """
        # 1. Buscamos si ya existe la relación
        statement = select(Favorito).where(
            Favorito.usuario_id == usuario_id,
            Favorito.cancion_id == cancion_id
        )
        favorito_existente = self.session.exec(statement).first()

        if favorito_existente:
            # BORRAR (Dislike)
            self.session.delete(favorito_existente)
            self.session.commit()
            return False
        else:
            # CREAR (Like)
            nuevo_favorito = Favorito(usuario_id=usuario_id, cancion_id=cancion_id)
            self.session.add(nuevo_favorito)
            self.session.commit()
            return True

    def obtener_ids_favoritos(self, usuario_id: int):
        """Devuelve una lista con los IDs de las canciones que le gustan al usuario"""
        statement = select(Favorito.cancion_id).where(Favorito.usuario_id == usuario_id)
        return self.session.exec(statement).all()