#SE HIZO TODO LO DE ROUTES DE GENEROS
from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from database.connection import engine
from models.generos import Genero, GeneroCreate, GeneroRead, GeneroUpdate

router = APIRouter(prefix="/generos", tags=["Géneros"])

@router.post("/", response_model=GeneroRead, status_code=201)
def crear_genero(genero: GeneroCreate):
    with Session(engine) as session:   
        nuevo_genero= Genero(**genero.model_dump())
        session.add(nuevo_genero)
        session.commit()
        session.refresh(nuevo_genero)
        return nuevo_genero

@router.get("/")
def obtener_generos():
    with Session(engine) as session:
        generos = session.exec(select(Genero).where(Genero.activo == True)).all()
        return generos

@router.get("/inactivos")
def obtener_inactivos():
    with Session(engine) as session:
        generos = session.exec(select(Genero).where(Genero.activo == False)).all()
        return generos

@router.get("/{id_genero}", response_model=GeneroRead)
def obtener_genero(id_genero: int):
    with Session(engine) as session:
        genero = session.get(Genero, id_genero)
        if not genero:
            raise HTTPException(status_code=404, detail="Género no encontrado")
        return genero
    
@router.get("/nombre/{nombre}", response_model=list[GeneroRead])
def obtener_genero_por_nombre(nombre:str):
    with Session(engine) as session:
        statement= select(Genero).where(Genero.nombre.ilike(f"%{nombre}"))
        genero = session.exec(statement).all()
        if not genero:
            raise HTTPException(status_code=404, detail="Género no encontrado con ese nombre")
        return genero
        
@router.put("/{id_genero}")
def actualizar_genero(id_genero: int, genero: GeneroUpdate):
    with Session(engine) as session:
        db_genero = session.get(Genero, id_genero)
        if not db_genero:
            raise HTTPException(status_code=404, detail="Género no encontrado")

        datos_actualizados = genero.dict(exclude_unset=True)
        for campo, valor in datos_actualizados.items():
            if valor in (None, "", " "):
                continue
            setattr(db_genero, campo, valor)

        session.add(db_genero)
        session.commit()
        session.refresh(db_genero)
        return {"mensaje": "Género actualizado correctamente", "genero": db_genero}


@router.delete("/{id_genero}")
def eliminar_genero(id_genero: int):
    with Session(engine) as session:
        genero = session.get(Genero, id_genero)
        if not genero:
            raise HTTPException(status_code=404, detail="Género no encontrado")
        genero.activo = False
        session.add(genero)
        session.commit()
        return {"mensaje": "Género eliminado correctamente"}

"""
@router.put("/{id_genero}/restaurar")
def restaurar_genero(id_genero: int):
    with Session(engine) as session:
        genero = session.get(Genero, id_genero)
        if not genero:
            raise HTTPException(status_code=404, detail="Género no encontrado")
        genero.activo = True
        session.add(genero)
        session.commit()
        return {"mensaje": "Género restaurado correctamente"}
"""