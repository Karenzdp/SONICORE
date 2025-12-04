from fastapi import APIRouter, Depends, HTTPException, Form
from sqlmodel import Session, select
from typing import Optional

from app.dependencies import get_session
from app.repositories.canciones_repo import CancionRepository
from app.models.canciones import Cancion, CancionRead
from app.models.artistas import Artista
from app.models.albumes import Album
from app.models.generos import Genero

router = APIRouter(prefix="/canciones", tags=["Canciones"])


# ============================================================================
# VALIDACIONES
# ============================================================================
def validar_duracion(duracion: str) -> bool:
    """Valida formato MM:SS y que segundos < 60"""
    import re
    match = re.match(r'^(\d+):(\d{2})$', duracion)
    if not match:
        return False
    mins, secs = match.groups()
    return int(secs) < 60


# ============================================================================
# CRUD ENDPOINTS
# ============================================================================

@router.post("/", status_code=201)
async def crear_cancion(
        titulo: str = Form(...),
        duracion: str = Form(...),
        artista_id: int = Form(...),
        album_id: Optional[int] = Form(None),
        genero_id: int = Form(1),
        anio_lanzamiento: Optional[int] = Form(None),  # ⚠️ CAMBIO AQUÍ
        session: Session = Depends(get_session)
):
    """✅ CREAR NUEVA CANCIÓN"""

    # Validaciones...
    if not titulo or not titulo.strip():
        raise HTTPException(status_code=400, detail="El título es obligatorio")

    import re
    match = re.match(r'^(\d+):(\d{2})$', duracion)
    if not match:
        raise HTTPException(
            status_code=400,
            detail="Formato de duración inválido. Usa MM:SS (ej: 3:45)"
        )
    if int(match.group(2)) >= 60:
        raise HTTPException(
            status_code=400,
            detail="Los segundos deben ser menores a 60"
        )

    # Validar artista
    if not session.get(Artista, artista_id):
        raise HTTPException(status_code=400, detail=f"El Artista ID {artista_id} no existe")

    # Validar álbum (opcional)
    if album_id and not session.get(Album, album_id):
        raise HTTPException(status_code=400, detail=f"El Álbum ID {album_id} no existe")

    # Crear canción
    repo = CancionRepository(session)
    nueva_cancion = Cancion(
        titulo=titulo.strip(),
        duracion=duracion,
        artista_id=artista_id,
        album_id=album_id,
        genero_id=genero_id,
        anio_lanzamiento=anio_lanzamiento  # ⚠️ NOMBRE CORRECTO
    )

    cancion_creada = repo.create(nueva_cancion)

    return {
        "mensaje": "✅ Canción creada exitosamente",
        "id": cancion_creada.id_cancion,
        "titulo": cancion_creada.titulo
    }
# app/routers/canciones_router.py

@router.put("/{id_cancion}")
async def actualizar_cancion(
        id_cancion: int,
        titulo: str = Form(...),
        duracion: str = Form(...),
        artista_id: int = Form(...),
        album_id: Optional[int] = Form(None),
        genero_id: int = Form(1),
        anio_lanzamiento: Optional[int] = Form(None),  # ⚠️ CAMBIO AQUÍ
        session: Session = Depends(get_session)
):
    """✏️ ACTUALIZAR CANCIÓN"""
    try:
        print(f"\n{'=' * 50}")
        print(f"🔧 ACTUALIZANDO CANCIÓN ID: {id_cancion}")
        print(f"📝 Datos recibidos:")
        print(f"   - titulo: {titulo}")
        print(f"   - duracion: {duracion}")
        print(f"   - artista_id: {artista_id}")
        print(f"   - album_id: {album_id}")
        print(f"   - genero_id: {genero_id}")
        print(f"   - anio_lanzamiento: {anio_lanzamiento}")

        # 1️⃣ Verificar que existe
        repo = CancionRepository(session)
        cancion = repo.get_by_id(id_cancion)
        if not cancion:
            print(f"❌ Canción {id_cancion} no encontrada")
            raise HTTPException(status_code=404, detail="Canción no encontrada")

        print(f"✅ Canción encontrada: {cancion.titulo}")

        # 2️⃣ Validar título
        if not titulo or not titulo.strip():
            print("❌ Título vacío")
            raise HTTPException(status_code=400, detail="El título es obligatorio")

        # 3️⃣ Validar duración
        import re
        match = re.match(r'^(\d+):(\d{2})$', duracion)
        if not match:
            print(f"❌ Duración inválida: {duracion}")
            raise HTTPException(
                status_code=400,
                detail="Formato de duración inválido. Usa MM:SS (ej: 3:45)"
            )
        if int(match.group(2)) >= 60:
            print(f"❌ Segundos >= 60")
            raise HTTPException(
                status_code=400,
                detail="Los segundos deben ser menores a 60"
            )

        # 4️⃣ Validar artista
        artista = session.get(Artista, artista_id)
        if not artista:
            print(f"❌ Artista {artista_id} no existe")
            raise HTTPException(
                status_code=400,
                detail=f"El Artista ID {artista_id} no existe"
            )

        print(f"✅ Artista válido: {artista.nombre}")

        # 5️⃣ Validar álbum (opcional)
        if album_id:
            album = session.get(Album, album_id)
            if not album:
                print(f"❌ Álbum {album_id} no existe")
                raise HTTPException(
                    status_code=400,
                    detail=f"El Álbum ID {album_id} no existe"
                )
            print(f"✅ Álbum válido: {album.nombre}")

        # 6️⃣ Actualizar campos
        cancion.titulo = titulo.strip()
        cancion.duracion = duracion
        cancion.artista_id = artista_id
        cancion.album_id = album_id
        cancion.genero_id = genero_id
        cancion.anio_lanzamiento = anio_lanzamiento  # ⚠️ NOMBRE CORRECTO

        print(f"💾 Guardando en BD...")
        session.add(cancion)
        session.commit()
        session.refresh(cancion)

        print(f"✅ Canción actualizada exitosamente")
        print(f"{'=' * 50}\n")

        return {
            "mensaje": "✅ Canción actualizada exitosamente",
            "id": cancion.id_cancion,
            "titulo": cancion.titulo
        }

    except HTTPException:
        raise

    except Exception as e:
        print(f"\n🔥 ERROR CRÍTICO:")
        print(f"   {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        print(f"{'=' * 50}\n")

        raise HTTPException(
            status_code=500,
            detail=f"Error interno: {str(e)}"
        )

@router.get("/{id_cancion}", response_model=CancionRead)
def obtener_cancion(id_cancion: int, session: Session = Depends(get_session)):
    """
    📖 LEER UNA CANCIÓN
    """
    cancion = CancionRepository(session).get_by_id(id_cancion)
    if not cancion:
        raise HTTPException(status_code=404, detail="Canción no encontrada")
    return cancion


@router.get("/{id_cancion}/detalle")
async def obtener_datos_completos(
        id_cancion: int,
        session: Session = Depends(get_session)
):
    """
    📊 OBTENER DATOS ENRIQUECIDOS PARA EL MODAL
    Incluye: Artista, Álbum, Género, Foto
    """
    cancion = session.get(Cancion, id_cancion)
    if not cancion:
        raise HTTPException(status_code=404, detail="Canción no encontrada")

    # Cargar relaciones
    artista = session.get(Artista, cancion.artista_id) if cancion.artista_id else None
    album = session.get(Album, cancion.album_id) if cancion.album_id else None
    genero = session.get(Genero, cancion.genero_id) if cancion.genero_id else None

    # Determinar foto (prioridad: álbum > artista > placeholder)
    foto = None
    if album and album.foto_portada:
        foto = album.foto_portada
    elif artista and artista.foto:
        foto = artista.foto

    return {
        "id": cancion.id_cancion,
        "titulo": cancion.titulo,
        "duracion": cancion.duracion,
        "anio": cancion.anio,
        "artista_id": cancion.artista_id,
        "artista_nombre": artista.nombre if artista else "Desconocido",
        "album_id": cancion.album_id,
        "album_nombre": album.nombre if album else "Sencillo",
        "genero_id": cancion.genero_id,
        "genero_nombre": genero.nombre if genero else "General",
        "foto": foto
    }


@router.delete("/{id_cancion}")
def eliminar_cancion(id_cancion: int, session: Session = Depends(get_session)):
    """
    🗑️ ELIMINAR CANCIÓN (SOFT DELETE)
    """
    repo = CancionRepository(session)
    if not repo.soft_delete(id_cancion):
        raise HTTPException(status_code=404, detail="Canción no encontrada")
    return {"mensaje": "✅ Canción eliminada exitosamente"}