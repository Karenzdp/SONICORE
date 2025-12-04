from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from sqlmodel import Session, select
from typing import List, Optional

from app.dependencies import get_session
from app.models.generos import Genero, GeneroRead
from app.models.albumes import Album
from app.models.canciones import Cancion
from app.services.supabase_service import SupabaseService

router = APIRouter(prefix="/generos", tags=["Géneros"])


# --- 1. OBTENER DETALLE ---
@router.get("/{id_genero}/detalle")
def obtener_detalle_genero(id_genero: int, session: Session = Depends(get_session)):
    genero = session.get(Genero, id_genero)
    if not genero:
        raise HTTPException(status_code=404, detail="Género no encontrado")

    albumes = session.exec(select(Album).where(Album.genero_id == id_genero)).all()
    canciones = session.exec(select(Cancion).where(Cancion.genero_id == id_genero).limit(10)).all()

    return {
        "id": genero.id_genero,
        "nombre": genero.nombre,
        "descripcion": genero.descripcion,
        "foto": getattr(genero, "foto", None),  # Asumiendo que agregaste el campo 'foto' a tu modelo Genero
        "albumes": [{"id": a.id_album, "nombre": a.nombre, "foto": a.foto_portada, "anio": a.anio_lanzamiento} for a in
                    albumes],
        "canciones": [{"id": c.id_cancion, "titulo": c.titulo, "duracion": c.duracion} for c in canciones]
    }


# --- 2. CREAR GÉNERO (AHORA CON FOTO) ---
@router.post("/")
async def crear_genero(
        nombre: str = Form(...),
        descripcion: str = Form(None),
        foto_file: UploadFile = File(None),
        session: Session = Depends(get_session)
):
    # Subir foto si existe
    url_foto = None
    if foto_file and foto_file.filename:
        try:
            supa = SupabaseService()
            contenido = await foto_file.read()
            url_foto = supa.subir_imagen(contenido, foto_file.content_type, "generos")
        except Exception as e:
            print(f"⚠️ Error foto genero: {e}")

    # Nota: Asegúrate de que tu modelo Genero tenga el campo 'foto'
    # Si no lo tiene en la BD, esto fallará al guardar.
    nuevo = Genero(nombre=nombre, descripcion=descripcion)
    if url_foto:
        # Hack dinámico por si el modelo no tiene el campo tipado aún
        setattr(nuevo, "foto", url_foto)

    session.add(nuevo)
    session.commit()
    session.refresh(nuevo)
    return nuevo


# --- 3. ACTUALIZAR GÉNERO (AHORA CON FOTO) ---
@router.put("/{id_genero}")
async def actualizar_genero(
        id_genero: int,
        nombre: str = Form(...),
        descripcion: str = Form(None),
        foto_file: UploadFile = File(None),
        session: Session = Depends(get_session)
):
    genero = session.get(Genero, id_genero)
    if not genero:
        raise HTTPException(status_code=404, detail="No encontrado")

    genero.nombre = nombre
    if descripcion is not None:
        genero.descripcion = descripcion

    if foto_file and foto_file.filename:
        try:
            supa = SupabaseService()
            contenido = await foto_file.read()
            url = supa.subir_imagen(contenido, foto_file.content_type, "generos")
            setattr(genero, "foto", url)
        except:
            pass

    session.add(genero)
    session.commit()
    session.refresh(genero)
    return {"mensaje": "Género actualizado"}


# --- 4. ELIMINAR ---
@router.delete("/{id_genero}")
def eliminar_genero(id_genero: int, session: Session = Depends(get_session)):
    genero = session.get(Genero, id_genero)
    if not genero:
        raise HTTPException(status_code=404, detail="No encontrado")
    session.delete(genero)
    session.commit()
    return {"mensaje": "Género eliminado"}