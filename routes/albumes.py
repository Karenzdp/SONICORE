#FALTA GET POR AÑO DE LANZAMIENTO
from datetime import date
from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from models.generos import Genero
from models.artistas import Artista
from database.connection import engine
from models.albumes import Album, AlbumCreate, AlbumRead, AlbumUpdate

router = APIRouter(prefix="/albunes", tags=["lÁbumes"])


@router.post("/", response_model=AlbumRead, status_code=201)
def crear_album(album: AlbumCreate):
    with Session(engine) as session:
        errores = []

        artista = session.get(Artista, album.artista_principal_id)
        if not artista:
            errores.append("El artista principal especificado no existe.")

        genero = session.get(Genero, album.genero_id)
        if not genero:
            errores.append("El género especificado no existe.")

        if errores:
            raise HTTPException(status_code=400, detail=errores)

        nuevo_album = Album(**album.model_dump())
        session.add(nuevo_album)
        session.commit()
        session.refresh(nuevo_album)
        return nuevo_album



@router.get("/")
def obtener_albumes():
    with Session(engine) as session:
        albumes = session.exec(select(Album).where(Album.activo == True)).all()
        return albumes

@router.get("/inactivos")
def obtener_inactivos():
    with Session(engine) as session:
        albunes = session.exec(select(Album).where(Album.activo == False)).all()
        return albunes

#Obtener álbum por ID
@router.get("/{id_album}", response_model=AlbumRead)
def obtener_album(id_album: int):
    with Session(engine) as session:
        album = session.get(Album, id_album)
        if not album:
            raise HTTPException(status_code=404, detail="Álbum no encontrado")
        return album


#Buscar álbum por nombre
@router.get("/buscar/nombre/{nombre}", response_model=list[AlbumRead])
def buscar_album_por_nombre(nombre: str):
    with Session(engine) as session:
        albunes = session.exec(select(Album).where(Album.nombre.ilike(f"%{nombre}%"))).all()
        if not albunes:
            raise HTTPException(status_code=404, detail="No se encontraron álbumes con ese nombre")
        return albunes


#Buscar álbumes por artista
@router.get("/buscar/artista/{artista_id}", response_model=list[AlbumRead])
def buscar_albumes_por_artista(artista_id: int):
    with Session(engine) as session:
        albunes = session.exec(select(Album).where(Album.artista_principal_id == artista_id)).all()
        if not albunes:
            raise HTTPException(status_code=404, detail="No se encontraron álbumes para este artista")
        return albunes


# Actualizar álbum
@router.put("/{id_album}")
def actualizar_album(id_album: int, album: AlbumUpdate):
    with Session(engine) as session:
        db_album = session.get(Album, id_album)
        if not db_album:
            raise HTTPException(status_code=404, detail="Álbum no encontrado")

        datos_actualizados = album.dict(exclude_unset=True)
        for campo, valor in datos_actualizados.items():
            if valor in (None, "", " "):
                continue
            if campo == "fecha_lanzamiento" and isinstance(valor, str):
                try:
                    valor = date.fromisoformat(valor)
                except ValueError:
                    raise HTTPException(status_code=400, detail="Formato de fecha inválido (usa YYYY-MM-DD)")
            setattr(db_album, campo, valor)

        session.add(db_album)
        session.commit()
        session.refresh(db_album)
        return {"mensaje": "Álbum actualizado correctamente", "album": db_album}


# Eliminar álbum
@router.delete("/{id_album}")
def eliminar_album(id_album: int):
    with Session(engine) as session:
        album = session.get(Album, id_album)
        if not album:
            raise HTTPException(status_code=404, detail="Álbum no encontrado")
        album.activo = False
        session.add(album)
        session.commit()
        return {"mensaje": "Álbum eliminado correctamente"}
"""
@router.put("/{id_album}/restaurar")
def restaurar_album(id_album: int):
    with Session(engine) as session:
        album = session.get(Album, id_album)
        if not album:
            raise HTTPException(status_code=404, detail="Álbum no encontrado")
        album.activo = True
        session.add(album)
        session.commit()
        return {"mensaje": "Álbum restaurado correctamente"}
"""