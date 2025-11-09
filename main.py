from fastapi import FastAPI
from database.database import create_db_and_tables
from database.database import engine
from sqlalchemy import text

with engine.connect() as connection:
    result = connection.execute(text("SELECT version();"))
    for row in result:
        print(f"✅ Conectado a: {row}")

from routes.artistas import router as artistas
from routes.generos import router as generos
from routes.albumes import router as albumes
from routes.canciones import router as canciones
from routes.api import router as apis
from routes.usuario import router as usuarios

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    

app.include_router(usuarios, prefix="/usuarios", tags=["Usuarios"])
app.include_router(artistas, prefix="/artistas", tags=["Artistas"])
app.include_router(generos, prefix="/generos", tags=["Géneros"])
app.include_router(albumes, prefix="/albumes", tags=["Álbumes"])
app.include_router(canciones, prefix="/canciones", tags=["Canciones"])
app.include_router(apis, prefix="/apis", tags=["APIs Externas"])

@app.get("/")
def read_root():
    return {"mensaje": "Bienvenido a SONICORE - API DE MÚSICA"}

