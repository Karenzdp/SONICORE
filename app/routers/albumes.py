from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlmodel import Session, delete
from sqlalchemy.exc import IntegrityError  # <--- IMPORTANTE: Para atrapar el error de ID no existente
from typing import List, Optional

from app.dependencies import get_session
from app.repositories.albumes_repo import AlbumRepository
from app.models.albumes import Album, AlbumRead
from app.models.canciones import Cancion
from app.services.supabase_service import SupabaseService
from app.services.music_service import MusicService

router = APIRouter(prefix="/albunes", tags=["Álbumes"])


# --- 1. CREAR ÁLBUM (POST) ---
@router.post("/", status_code=201)
async def crear_album(
        nombre: str = Form(...),
        anio_lanzamiento: int = Form(...),
        artista_principal_id: int = Form(...),
        descripcion: Optional[str] = Form(None),
        genero_id: int = Form(1),
        canciones_texto: str = Form(""),
        foto_file: UploadFile = File(None),
        foto_portada: Optional[str] = Form(None),
        session: Session = Depends(get_session)
):
    # 1. Subir Foto
    url_final = foto_portada
    if foto_file and foto_file.filename:
        try:
            supa = SupabaseService()
            contenido = await foto_file.read()
            url_final = supa.subir_imagen(contenido, foto_file.content_type, "albumes")
        except Exception as e:
            print(f"⚠️ Error subiendo foto: {e}")

    try:
        # 2. Crear en BD
        repo = AlbumRepository(session)
        nuevo_album = repo.crear_album(
            titulo=nombre,
            artista_id=artista_principal_id,
            anio=anio_lanzamiento,
            cover=url_final,
            genero_id=genero_id
        )

        if descripcion:
            nuevo_album.descripcion = descripcion
            session.add(nuevo_album)

        session.commit()  # Intentamos guardar el álbum primero

        # 3. Procesar Canciones
        if canciones_texto and canciones_texto.strip():
            ms = MusicService(session)
            ms._procesar_canciones_texto(
                artista_id=artista_principal_id,
                album_id=nuevo_album.id_album,
                texto=canciones_texto,
                genero_id=genero_id
            )

        return nuevo_album

    except IntegrityError as e:
        session.rollback()
        error_msg = str(e.orig)
        if "artista_principal_id" in error_msg:
            raise HTTPException(400, f"El Artista con ID {artista_principal_id} no existe.")
        if "genero_id" in error_msg:
            raise HTTPException(400, f"El Género con ID {genero_id} no existe.")
        raise HTTPException(400, "Error de base de datos: Datos inválidos.")


# --- 2. ACTUALIZAR ÁLBUM (PUT) - BLINDADO ---
@router.put("/{id_album}")
async def actualizar_album(
        id_album: int,
        nombre: str = Form(...),
        anio_lanzamiento: int = Form(...),
        artista_principal_id: Optional[int] = Form(None),
        descripcion: Optional[str] = Form(None),
        canciones_texto: Optional[str] = Form(None),
        foto_file: Optional[UploadFile] = File(None),
        genero_id: int = Form(1),
        session: Session = Depends(get_session)
):
    repo = AlbumRepository(session)
    album_db = repo.get_by_id(id_album)
    if not album_db:
        raise HTTPException(status_code=404, detail="Álbum no encontrado")

    # Actualizar campos
    album_db.nombre = nombre
    album_db.anio_lanzamiento = anio_lanzamiento
    album_db.genero_id = genero_id

    if artista_principal_id: album_db.artista_principal_id = artista_principal_id
    if descripcion is not None: album_db.descripcion = descripcion

    # Foto
    if foto_file and foto_file.filename:
        try:
            supa = SupabaseService()
            contenido = await foto_file.read()
            album_db.foto_portada = supa.subir_imagen(contenido, foto_file.content_type, "albumes")
        except:
            pass

    try:
        session.add(album_db)
        session.commit()
        session.refresh(album_db)

        # Actualizar Canciones
        if canciones_texto is not None:
            session.exec(delete(Cancion).where(Cancion.album_id == id_album))
            if canciones_texto.strip():
                ms = MusicService(session)
                # Usamos el ID de artista que acabamos de guardar/validar
                ms._procesar_canciones_texto(
                    artista_id=album_db.artista_principal_id,
                    album_id=id_album,
                    texto=canciones_texto,
                    genero_id=album_db.genero_id
                )
            session.commit()

        return {"mensaje": "Actualizado"}

    except IntegrityError as e:
        session.rollback()
        error_msg = str(e.orig)
        # DETECTAR QUÉ ID FALLÓ PARA DAR MENSAJE CLARO
        if "artista_principal_id" in error_msg:
            raise HTTPException(400, f"Error: El Artista ID {artista_principal_id} no existe.")
        if "genero_id" in error_msg:
            raise HTTPException(400, f"Error: El Género ID {genero_id} no existe.")
        raise HTTPException(400, "Error al guardar: Verifica los IDs ingresados.")


# --- GET / DELETE ---
@router.get("/", response_model=List[AlbumRead])
def obtener_todos(session: Session = Depends(get_session)):
    return AlbumRepository(session).get_all()


@router.get("/{id_album}", response_model=AlbumRead)
def obtener_uno(id_album: int, session: Session = Depends(get_session)):
    return AlbumRepository(session).get_by_id(id_album)


@router.delete("/{id_album}")
def eliminar_album(id_album: int, session: Session = Depends(get_session)):
    session.exec(delete(Cancion).where(Cancion.album_id == id_album))
    session.commit()
    if not AlbumRepository(session).soft_delete(id_album):
        raise HTTPException(404, "No encontrado")
    return {"mensaje": "Eliminado"}