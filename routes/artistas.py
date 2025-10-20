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
                    status_code=400, detail="El género indicado no existe, no se puede crear el artista"
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

# OBTENER POR ID
@router.get("/{id_artista}", response_model=ArtistaRead)
def obtener_artista(id_artista: int):
    with Session(engine) as session:
        artista = session.get(Artista, id_artista)
        if not artista:
            raise HTTPException(status_code=404, detail="Artista no encontrado")
        return artista
    
    
#OBTENER POR NOMBRE
@router.get("/nombre/{nombre}", response_model=list[ArtistaRead])
def obtener_artista_por_nombre(nombre:str):
    with Session(engine) as session:
        statement = select(Artista).where(Artista.nombre.ilike(f"%{nombre}%"))#cambie la f
        artista = session.exec(statement).all()
        if not artista:
            raise HTTPException(status_code=404, detail="Artista no encontrado con ese nombre")
        return artista


#OBTENER POR NACIONALIDAD  
@router.get("/nacionalidad/{nacionalidad}", response_model=list[ArtistaRead])
def obtener_artista_por_nacionalidad(nacionalidad:str):
    with Session(engine) as session:
        statement = select(Artista).where(Artista.nacionalidad.ilike(f"%{nacionalidad}%"))
        artista = session.exec(statement).all()
        if not artista:
            raise HTTPException(status_code=404, detail="Artista no encontrado con esa nacionalidad")
        return artista
    
#OBTENER POR ID DE GENERO 
@router.get("/id_genero/{genero_id}", response_model=list[ArtistaRead])    
def obtener_artista_por_ID_genero(genero_id: int):
    with Session(engine) as session:
        statement = select(Artista).where(Artista.genero_principal_id == genero_id)
        artista = session.exec(statement).all()
        if not artista:
            raise HTTPException(status_code=404, detail="Artista no encontrado con ese ID de género")
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
        return {"mensaje": "Artista eliminado correctamente"}