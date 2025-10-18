from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from database.connection import engine
from models.artistas import Artista, ArtistaCreate, ArtistaRead
from models.generos import Genero

router = APIRouter(prefix="/artistas", tags=["Artistas"])

# Crear artista
@router.post("/", response_model=ArtistaRead, status_code=201)
def crear_artista(artista: ArtistaCreate):
    with Session(engine) as session:
        # 🔹 Validar que el género exista (si se envió un ID)
        if artista.genero_principal_id is not None:
            genero = session.get(Genero, artista.genero_principal_id)
            if not genero:
                raise HTTPException(
                    status_code=400, detail="El género indicado no existe"
                )

        nuevo_artista = Artista(**artista.model_dump())
        session.add(nuevo_artista)
        session.commit()
        session.refresh(nuevo_artista)
        return nuevo_artista


# Listar todos
@router.get("/", response_model=list[ArtistaRead])
def obtener_artistas():
    with Session(engine) as session:
        artistas = session.exec(select(Artista)).all()
        return artistas

# Obtener por ID
@router.get("/{id_artista}", response_model=ArtistaRead)
def obtener_artista(id_artista: int):
    with Session(engine) as session:
        artista = session.get(Artista, id_artista)
        if not artista:
            raise HTTPException(status_code=404, detail="Artista no encontrado")
        return artista

# Actualizar artista
@router.put("/{id_artista}", response_model=ArtistaRead)
def actualizar_artista(id_artista: int, datos: ArtistaCreate):  # ✅ Usar ArtistaCreate
    with Session(engine) as session:
        artista_db = session.get(Artista, id_artista)
        if not artista_db:
            raise HTTPException(status_code=404, detail="Artista no encontrado")

        # Actualizar solo los campos enviados
        datos_dict = datos.model_dump(exclude_unset=True)
        
        for k, v in datos_dict.items():
            setattr(artista_db, k, v)

        session.add(artista_db)
        session.commit()
        session.refresh(artista_db)
        return artista_db

# Eliminar
@router.delete("/{id_artista}", status_code=204)
def eliminar_artista(id_artista: int):
    with Session(engine) as session:
        artista = session.get(Artista, id_artista)
        if not artista:
            raise HTTPException(status_code=404, detail="Artista no encontrado")
        
        session.delete(artista)
        session.commit()
        return None  # ✅ 204 No Content no debe retornar body