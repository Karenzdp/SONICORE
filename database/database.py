from sqlmodel import SQLModel, create_engine
from dotenv import load_dotenv
import os

# ✅ 1. Cargar variables del archivo .env
# Esto permite usar credenciales seguras desde Clever Cloud o localmente
load_dotenv()

# ✅ 2. Intentar primero conexión a PostgreSQL (Clever Cloud)
DATABASE_URL = os.getenv("POSTGRESQL_ADDON_URI")

# ✅ 3. Si no existe la variable (modo local), usar SQLite
if not DATABASE_URL:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///sonicore_prueba.db")

# ✅ 4. Crear el motor de conexión con SQLModel
# echo=True muestra en consola las consultas SQL ejecutadas
engine = create_engine(DATABASE_URL, echo=True)

# ✅ 5. Función para crear las tablas al iniciar la app
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
