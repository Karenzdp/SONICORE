from datetime import date
from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from database.connection import engine
from models.artistas import Artista, ArtistaCreate, ArtistaRead, ArtistaUpdate
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
        if not genero.activo:
                raise HTTPException(
                    status_code=400, 
                    detail="El género seleccionado está inactivo, no se puede crear el artista"
                )
        nuevo_artista = Artista(**artista.model_dump())
        session.add(nuevo_artista)
        session.commit()
        session.refresh(nuevo_artista)
        return nuevo_artista


@router.get("/")
def obtener_artistas():
    with Session(engine) as session:
        artistas = session.exec(select(Artista).where(Artista.activo == True)).all()
        return artistas

# Obtener artistas inactivos (papelera)
@router.get("/inactivos")
def obtener_inactivos():
    with Session(engine) as session:
        artistas = session.exec(select(Artista).where(Artista.activo == False)).all()
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
@router.put("/{id_artista}")
def actualizar_artista(id_artista: int, artista: ArtistaUpdate):
    with Session(engine) as session:
        db_artista = session.get(Artista, id_artista)
        if not db_artista:
            raise HTTPException(status_code=404, detail="Artista no encontrado")

        datos_actualizados = artista.dict(exclude_unset=True)

        for campo, valor in datos_actualizados.items():
            if valor in (None, "", " "):  # Ignora campos vacíos
                continue
            if campo == "fecha_nacimiento" and isinstance(valor, str):
                try:
                    valor = date.fromisoformat(valor)
                except ValueError:
                    raise HTTPException(status_code=400, detail="Formato de fecha inválido (usa YYYY-MM-DD)")
            setattr(db_artista, campo, valor)

        session.add(db_artista)
        session.commit()
        session.refresh(db_artista)

        return {"mensaje": "Artista actualizado correctamente", "artista": db_artista}

# Eliminar
@router.delete("/{id_artista}")
def eliminar_artista(id_artista: int):
    with Session(engine) as session:
        artista = session.get(Artista, id_artista)
        if not artista:
            raise HTTPException(status_code=404, detail="Artista no encontrado")
        artista.activo = False
        session.add(artista)
        session.commit()
        
        return {"mensaje": "Artista eliminado correctamente"}

"""
# Restaurar artista
@router.put("/{id_artista}/restaurar")
def restaurar_artista(id_artista: int):
    with Session(engine) as session:
        artista = session.get(Artista, id_artista)
        if not artista:
            raise HTTPException(status_code=404, detail="Artista no encontrado")
        artista.activo = True
        session.add(artista)
        session.commit()
        return {"mensaje": "Artista restaurado correctamente"}
"""