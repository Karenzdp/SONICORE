from fastapi import FastAPI
from database.connection import create_db_and_tables
from routes.artistas import router as artistas
from routes.generos import router as generos
from routes.albumes import router as albumes
from routes.canciones import router as canciones
from routes.api import router as apis
app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(artistas)
app.include_router(generos)
app.include_router(albumes)
app.include_router(canciones)
app.include_router(apis)
@app.get("/")
def read_root():
    return {"mensaje": "Bienvenido a SONICORE - API DE MÚSICA"}

