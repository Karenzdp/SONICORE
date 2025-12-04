import os
from sqlmodel import SQLModel, create_engine
from dotenv import load_dotenv


# Cargar variables de entorno desde .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Validación para que no explote si falta la URL
if not DATABASE_URL:
    raise ValueError("❌ Error: No se encontró DATABASE_URL en el archivo .env")

# Corrección para Heroku/Clever (si la URL empieza con postgres://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)


def create_db_and_tables():
    # Importamos todos los modelos aquí para que SQLModel los reconozca al crear tablas
    from app.models.usuario import Usuario
    from app.models.artistas import Artista
    from app.models.albumes import Album
    from app.models.canciones import Cancion
    from app.models.generos import Genero
    from app.models.favoritos import Favorito
    from app.models.api import API

    SQLModel.metadata.create_all(engine)