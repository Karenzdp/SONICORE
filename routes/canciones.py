from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from models.albumes import Album
from models.generos import Genero
from database.connection import engine
from models.canciones import Cancion, CancionCreate, CancionRead, CancionUpdate
from models.artistas import Artista, ArtistaUpdate
from datetime import date
router = APIRouter(prefix="/canciones", tags=["Canciones"])

@router.post("/", response_model=CancionRead)
def crear_cancion(cancion: CancionCreate):
    with Session(engine) as session:
        errores = []

        artista = session.get(Artista, cancion.artista_id)
        if not artista:
            errores.append("El artista especificado no existe.")

        genero = session.get(Genero, cancion.genero_id)
        if not genero:
            errores.append("El género especificado no existe.")

        if errores:
            raise HTTPException(status_code=400, detail=errores)

        nueva_cancion = Cancion(**cancion.model_dump())
        session.add(nueva_cancion)
        session.commit()
        session.refresh(nueva_cancion)
        return nueva_cancion


@router.get("/")
def obtener_canciones():
    with Session(engine) as session:
        canciones = session.exec(select(Cancion).where(Cancion.activo == True)).all()
        return canciones

@router.get("/inactivos")
def obtener_inactivos():
    with Session(engine) as session:
        canciones = session.exec(select(Cancion).where(Cancion.activo == False)).all()
        return canciones

@router.get("/{id_cancion}", response_model=CancionRead)
def obtener_cancion(id_cancion: int):
    with Session(engine) as session:
        cancion = session.get(Cancion, id_cancion)
        if not cancion:
            raise HTTPException(status_code=404, detail="Canción no encontrada")
        return cancion


@router.get("/buscar/{titulo}", response_model=list[CancionRead])
def buscar_cancion_por_titulo(titulo: str):
    with Session(engine) as session:
        query = select(Cancion).where(Cancion.titulo.ilike(f"%{titulo}%"))
        resultados = session.exec(query).all()
        if not resultados:
            raise HTTPException(status_code=404, detail="No se encontraron canciones con ese título")
        return resultados


@router.get("/artista/{id_artista}", response_model=list[CancionRead])
def buscar_por_artista(id_artista: int):
    with Session(engine) as session:
        query = select(Cancion).where(Cancion.artista_id == id_artista)
        resultados = session.exec(query).all()
        if not resultados:
            raise HTTPException(status_code=404, detail="No se encontraron canciones para este artista")
        return resultados


@router.get("/genero/{id_genero}", response_model=list[CancionRead])
def buscar_por_genero(id_genero: int):
    with Session(engine) as session:
        query = select(Cancion).where(Cancion.genero_id == id_genero)
        resultados = session.exec(query).all()
        if not resultados:
            raise HTTPException(status_code=404, detail="No se encontraron canciones para este género")
        return resultados


@router.put("/{id_cancion}")
def actualizar_cancion(id_cancion: int, cancion: CancionUpdate):
    with Session(engine) as session:
        db_cancion = session.get(Cancion, id_cancion)
        if not db_cancion:
            raise HTTPException(status_code=404, detail="Canción no encontrada")

        datos_actualizados = cancion.dict(exclude_unset=True)

        if "album_id" in datos_actualizados and datos_actualizados["album_id"] is not None:
            album = session.get(Album, datos_actualizados["album_id"])
            if not album:
                raise HTTPException(status_code=400, detail="El álbum especificado no existe")

        for campo, valor in datos_actualizados.items():
            if valor in (None, "", " "):
                continue
            if campo == "fecha_lanzamiento" and isinstance(valor, str):
                try:
                    valor = date.fromisoformat(valor)
                except ValueError:
                    raise HTTPException(status_code=400, detail="Formato de fecha inválido (usa YYYY-MM-DD)")
            setattr(db_cancion, campo, valor)

        session.add(db_cancion)
        session.commit()
        session.refresh(db_cancion)
        return {"mensaje": "Canción actualizada correctamente", "cancion": db_cancion}


@router.delete("/{id_cancion}")
def eliminar_cancion(id_cancion: int):
    with Session(engine) as session:
        cancion = session.get(Cancion, id_cancion)
        if not cancion:
            raise HTTPException(status_code=404, detail="Canción no encontrada")
        cancion.activo = False
        session.add(cancion)
        session.commit()
        return None
