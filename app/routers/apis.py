from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.dependencies import get_session

# Importamos los Modelos
from app.models.api import API, APICreate, APIRead, APIUpdate
# Importamos la Lógica de Negocio (POO)
from app.repositories.api_repo import APIRepository
from app.services.music_service import MusicService

# Mantenemos el prefijo /apis para no romper el HTML
router = APIRouter(prefix="/apis", tags=["Gestión de APIs e Importación"])


# --- RUTA DE IMPORTACIÓN (LA QUE ESTABA FALLANDO) ---
@router.post("/importar/{nombre_artista}")
def importar_desde_spotify(nombre_artista: str, session: Session = Depends(get_session)):
    """Recibe el nombre del artista y llama al servicio para importarlo"""
    try:
        # 1. Instanciamos el servicio pasándole la sesión de BD
        servicio = MusicService(session)

        # 2. Ejecutamos la importación
        resultado = servicio.importar_artista_desde_itunes(nombre_artista)

        # 3. Devolvemos la respuesta al JavaScript
        return resultado

    except Exception as e:
        print(f"❌ Error en ruta importar: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- TUS OTRAS RUTAS DE APIs (CRUD) ---
# (Las mantengo aquí para que no las pierdas)

@router.post("/", response_model=APIRead, status_code=201)
def crear_api(api: APICreate, session: Session = Depends(get_session)):
    repo = APIRepository(session)  # Asegúrate de tener el repo importado si usas esto
    # ... lógica simplificada o usar repositorio ...
    nueva_api = API.model_validate(api)
    session.add(nueva_api)
    session.commit()
    session.refresh(nueva_api)
    return nueva_api


# ... (Puedes dejar el resto de tus rutas de API aquí si las usas) .

@router.get("/", response_model=list[APIRead])
def listar_apis_configuradas(session: Session = Depends(get_session)):
    repo = APIRepository(session)
    return repo.get_all()


@router.put("/{id_api}")
def actualizar_api(id_api: int, datos: APIUpdate, session: Session = Depends(get_session)):
    repo = APIRepository(session)
    api = repo.get_by_id(id_api)
    if not api:
        raise HTTPException(status_code=404, detail="API no encontrada")

    # Actualización parcial
    data_dict = datos.model_dump(exclude_unset=True)
    for key, value in data_dict.items():
        setattr(api, key, value)

    return repo.create(api)  # Reutilizamos create para guardar cambios


@router.delete("/{id_api}")
def eliminar_api(id_api: int, session: Session = Depends(get_session)):
    repo = APIRepository(session)
    if not repo.soft_delete(id_api):
        raise HTTPException(status_code=404, detail="API no encontrada")
    return {"mensaje": "API desactivada correctamente"}

# ==========================================
# 2. PARTE DE ACCIÓN (El Servicio de Música)
# ==========================================

