from sqlmodel import Session, select
from fastapi import HTTPException
from passlib.context import CryptContext
from app.repositories.base import BaseRepository
from app.models.usuario import Usuario, UsuarioCreate

# Configuración de passlib para bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UsuarioRepository(BaseRepository[Usuario]):
    def __init__(self, session: Session):
        super().__init__(session, Usuario)

    def registrar(self, datos: UsuarioCreate) -> Usuario:
        # 🟢 CORRECCIÓN: Truncar la contraseña a 72 bytes antes de hashear (por la limitación de bcrypt)
        password_to_hash = datos.contrasena[:72]

        # Encriptación encapsulada
        hashed = pwd_context.hash(password_to_hash)

        nuevo = Usuario(nombre_usuario=datos.nombre_usuario, correo=datos.correo, contrasena=hashed)
        return self.create(nuevo)

    def login(self, username, password):
        # 1. Buscar usuario
        statement = select(Usuario).where(Usuario.nombre_usuario == username, Usuario.activo == True)
        user = self.session.exec(statement).first()

        # 🟢 CORRECCIÓN: Truncar la contraseña de entrada antes de verificar
        truncated_password = password[:72]

        # 2. Verificar existencia y contraseña
        if not user or not pwd_context.verify(truncated_password, user.contrasena):
            return None

        return user