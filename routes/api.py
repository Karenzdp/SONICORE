from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from database.connection import engine
from models.api import API, APICreate, APIRead, APIUpdate

router = APIRouter(prefix="/apis", tags=["APIs"])

# Crear API
@router.post("/", response_model=APIRead, status_code=201)
def crear_api(api: APICreate):
    with Session(engine) as session:
        nueva_api = API(**api.model_dump())
        session.add(nueva_api)
        session.commit()
        session.refresh(nueva_api)
        return nueva_api

@router.get("/", response_model=list[APIRead])
def obtener_apis():
    with Session(engine) as session:
        apis = session.exec(select(API)).all()
        return apis
    
@router.get("/inactivos")
def obtener_inactivos():
    with Session(engine) as session:
        apis = session.exec(select(API).where(API.activo == False)).all()
        if not apis:
            raise HTTPException(status_code=404, detail="No hay APIs inactivas")
        return apis

@router.get("/{id_api}", response_model=APIRead)
def obtener_api(id_api: int):
    with Session(engine) as session:
        api = session.get(API, id_api)
        if not api:
            raise HTTPException(status_code=404, detail="API no encontrada")
        return api

@router.put("/{id_api}")
def actualizar_api(id_api: int, datos: APIUpdate):
    with Session(engine) as session:
        api = session.get(API, id_api)
        if not api:
            raise HTTPException(status_code=404, detail="API no encontrada")

        datos_act = datos.dict(exclude_unset=True)
        for k, v in datos_act.items():
            if v in (None, "", " "):
                continue
            setattr(api, k, v)

        session.add(api)
        session.commit()
        session.refresh(api)
        return {"mensaje":"API Actualizada Correctamente", "api": api}

@router.delete("/{id_api}")
def eliminar_api(id_api: int):
    with Session(engine) as session:
        api = session.get(API, id_api)
        if not api:
            raise HTTPException(status_code=404, detail="API no encontrada")
        api.activo= False
        session.add(api)
        session.commit()
        return {"mensaje": "API Eliminada correctamente"}
