from fastapi import HTTPException

def not_found(entity: str):
    return HTTPException(status_code=404, detail=f"{entity} no encontrado")

def already_exists(entity: str):
    return HTTPException(status_code=400, detail=f"Ya existe un {entity} con ese nombre")

def inactive_entity(entity: str):
    return HTTPException(status_code=400, detail=f"{entity} está inactivo o no disponible")
