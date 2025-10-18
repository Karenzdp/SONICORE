from fastapi import FastAPI
from database.connection import create_db_and_tables
from routes.artistas import router as artistas
from routes.generos import router as generos
app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(artistas)
app.include_router(generos)
@app.get("/")
def read_root():
    return {"mensaje": "Bienvenido a SONICORE - API DE MÚSICA"}

