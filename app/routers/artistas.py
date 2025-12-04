from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from sqlmodel import Session, select
import json
from typing import List, Optional
from app.dependencies import get_session
from app.repositories.artistas_repo import ArtistaRepository
from app.models.artistas import Artista, ArtistaRead, ArtistaUpdate, ArtistaCreate
from app.services.supabase_service import SupabaseService
from app.services.music_service import MusicService

router = APIRouter(prefix="/artistas", tags=["Artistas"])

# app/routers/artistas.py

# ... (importaciones existentes) ...

# app/routers/artistas.py

# app/routers/artistas.py

@router.post("/", status_code=201)
async def crear_artista(
        request: Request,
        nombre: str = Form(...),
        nacionalidad: str = Form(None),
        biografia: str = Form(None),
        genero_principal_id: int = Form(1),
        foto_file: UploadFile = File(None),  # <--- AQUÍ DEBERÍA LLEGAR LA FOTO
        top_canciones_texto: str = Form(""),
        discografia_json: str = Form("[]"),
        session: Session = Depends(get_session)
):
    # 👇 DIAGNÓSTICO EN TERMINAL 👇
    print("------------------------------------------------")
    print(f"📥 INTENTO DE CREACIÓN: {nombre}")

    if foto_file:
        print(f"📸 FOTO RECIBIDA: {foto_file.filename} (Tipo: {foto_file.content_type})")
    else:
        print("⚠️ ALERTA: No llegó ningún archivo en 'foto_file'")

    print("------------------------------------------------")
    # 👆 FIN DIAGNÓSTICO 👆

    try:
        albumes_metadata = json.loads(discografia_json)
        form_data = await request.form()
        album_files = []
        for i in range(len(albumes_metadata)):
            field_name = f"album_file_{i}"
            file = form_data.get(field_name)
            if file and hasattr(file, 'filename'):
                album_files.append(file)
            else:
                album_files.append(None)

        servicio = MusicService(session)
        artista_id = await servicio.guardar_artista_completo_con_archivos(
            nombre=nombre,
            nacionalidad=nacionalidad,
            biografia=biografia,
            genero_principal_id=genero_principal_id,
            artist_file=foto_file,
            top_canciones_texto=top_canciones_texto,
            albums_metadata=albumes_metadata,
            albums_files=album_files
        )

        return {"mensaje": f"Artista {nombre} creado con éxito", "id": artista_id}

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Error JSON en discografía.")
    except Exception as e:
        print(f"❌ ERROR FATAL: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- 2. LISTAR TODOS (GET) ---
@router.get("/", response_model=List[ArtistaRead])
def obtener_todos(session: Session = Depends(get_session)):
    repo = ArtistaRepository(session)
    return repo.get_all()


"""
@router.get("/{id_artista}", response_model=ArtistaRead)
def obtener_uno(id_artista: int, session: Session = Depends(get_session)):
    repo = ArtistaRepository(session)
    artista = repo.get_by_id(id_artista)
    if not artista:
        raise HTTPException(status_code=404, detail="Artista no encontrado")
    return artista"""


# --- 4. ACTUALIZAR (PUT) - ¡ESTA FALTABA! ---
@router.put("/{id_artista}")
async def actualizar_artista(
        id_artista: int,
        request: Request,  # <--- NECESARIO PARA LEER LOS ARCHIVOS DINÁMICOS
        nombre: str = Form(...),
        nacionalidad: str = Form(None),
        biografia: str = Form(None),
        genero_principal_id: int = Form(1),
        foto_file: Optional[UploadFile] = File(None),
        top_canciones_texto: str = Form(""),  # <--- AHORA SÍ RECIBIMOS ESTO
        discografia_json: str = Form("[]"),  # <--- Y ESTO
        session: Session = Depends(get_session)
):
    # 1. DIAGNÓSTICO RÁPIDO
    print(f"🔄 RUTAS: Recibiendo actualización para ID {id_artista}")
    print(f"📄 Discografía JSON recibida: {discografia_json}")

    # 2. PROCESAR ARCHIVOS DE ÁLBUMES (Igual que en el Create)
    #    Como los nombres son dinámicos (album_file_0, album_file_1...),
    #    necesitamos leer el form data directamente.
    try:
        albumes_metadata = json.loads(discografia_json)
        form_data = await request.form()
        album_files = []

        # Sincronizamos los archivos con los metadatos
        for i in range(len(albumes_metadata)):
            field_name = f"album_file_{i}"
            file = form_data.get(field_name)
            # Verificamos si es un archivo válido
            if file and hasattr(file, 'filename'):
                album_files.append(file)
            else:
                album_files.append(None)

        # 3. LLAMAR AL SERVICIO "QUIRÚRGICO" QUE CREAMOS ANTES
        #    (Asegúrate de haber actualizado MusicService con el código de mi respuesta anterior)
        servicio = MusicService(session)

        # Usamos la función unificada guardar_o_actualizar_artista
        # Si no la tienes renombrada así en el service, usa la lógica equivalente.
        await servicio.guardar_o_actualizar_artista(
            id_artista=id_artista,
            nombre=nombre,
            nacionalidad=nacionalidad,
            biografia=biografia,
            genero_principal_id=genero_principal_id,
            artist_file=foto_file,
            top_canciones_texto=top_canciones_texto,
            albums_metadata=albumes_metadata,
            albums_files=album_files
        )

        return {"mensaje": "Artista actualizado correctamente", "id": id_artista}

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="El JSON de la discografía es inválido.")
    except Exception as e:
        print(f"❌ ERROR EN UPDATE: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


# --- 5. ELIMINAR (DELETE) - ¡ESTA FALTABA! ---
@router.delete("/{id_artista}")
def eliminar_artista(id_artista: int, session: Session = Depends(get_session)):
    repo = ArtistaRepository(session)
    # Primero borramos canciones y álbumes asociados para no romper la BD
    # (Opcional: Configurar CASCADE en la BD, pero manual es más seguro aquí)
    # ... (simplificado: asumimos que soft_delete se encarga o lanzamos error)

    if not repo.soft_delete(id_artista):
        raise HTTPException(status_code=404, detail="Artista no encontrado")
    return {"mensaje": "Eliminado correctamente"}