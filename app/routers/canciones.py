from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.dependencies import get_session
from app.repositories.canciones_repo import CancionRepository
from app.models.canciones import CancionRead, CancionCreate, CancionUpdate

router = APIRouter(prefix="/canciones", tags=["Canciones"])


# 1. Crear
@router.post("/", response_model=CancionRead)
def crear_cancion(cancion: CancionCreate, session: Session = Depends(get_session)):
    repo = CancionRepository(session)
    return repo.crear_validado(cancion)


# 2. Obtener Todas
@router.get("/", response_model=list[CancionRead])
def obtener_canciones(session: Session = Depends(get_session)):
    repo = CancionRepository(session)
    return repo.get_all()


# 3. Obtener por ID (Restaurado)
@router.get("/{id_cancion}", response_model=CancionRead)
def obtener_cancion(id_cancion: int, session: Session = Depends(get_session)):
    repo = CancionRepository(session)
    cancion = repo.get_by_id(id_cancion)
    if not cancion:
        raise HTTPException(status_code=404, detail="Canción no encontrada")
    return cancion


# 4. Buscar por Título (Nuevo)
@router.get("/buscar/{titulo}", response_model=list[CancionRead])
def buscar_cancion(titulo: str, session: Session = Depends(get_session)):
    repo = CancionRepository(session)
    return repo.buscar_por_titulo(titulo)


# 5. Actualizar (Restaurado)
@router.put("/{id_cancion}", response_model=CancionRead)
def actualizar_cancion(id_cancion: int, datos: CancionUpdate, session: Session = Depends(get_session)):
    repo = CancionRepository(session)
    cancion_db = repo.get_by_id(id_cancion)
    if not cancion_db:
        raise HTTPException(status_code=404, detail="Canción no encontrada")

    data_dict = datos.model_dump(exclude_unset=True)
    for key, value in data_dict.items():
        setattr(cancion_db, key, value)

    return repo.create(cancion_db)


# 6. Eliminar
@router.delete("/{id_cancion}")
def eliminar_cancion(id_cancion: int, session: Session = Depends(get_session)):
    repo = CancionRepository(session)
    if not repo.soft_delete(id_cancion):
        raise HTTPException(status_code=404, detail="Canción no encontrada")
    return {"mensaje": "Canción eliminada"}