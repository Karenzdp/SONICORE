from fastapi import APIRouter
from app.services.dataset_service import DatasetService

router = APIRouter(prefix="/reportes", tags=["Analytics"])
servicio = DatasetService()

@router.get("/generos")
def reporte_generos():
    return servicio.reporte_generos()

@router.get("/top")
def reporte_top():
    return servicio.top_historico()