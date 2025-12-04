from sqlmodel import SQLModel
from database.database import engine

# IMPORTANTE: Importar TODOS los modelos para que SQLModel sepa qué crear
from models.usuario import Usuario
from models.generos import Genero
from models.artistas import Artista
from models.albumes import Album
from models.canciones import Cancion
from models.api import API
from models.favoritos import Favorito # 👈 NUEVO

def reiniciar_todo():
    print("⏳ Conectando a PostgreSQL...")
    print("🗑️  Borrando todas las tablas viejas...")
    
    # Esto borra las tablas existentes
    SQLModel.metadata.drop_all(engine)
    
    print("✨ Creando tablas nuevas con los campos: foto_portada, descripcion, etc...")
    # Esto crea las tablas nuevas
    SQLModel.metadata.create_all(engine)
    
    print("✅ ¡LISTO! Base de datos actualizada.")

if __name__ == "__main__":
    reiniciar_todo()