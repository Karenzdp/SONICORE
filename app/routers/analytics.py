from fastapi import APIRouter, Depends, Request, Body
from sqlmodel import Session
from app.dependencies import get_session
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.post("/track")
async def track_event(
        request: Request,
        payload: dict = Body(...),
        session: Session = Depends(get_session)
):
    """
    Endpoint Genérico para recibir cualquier evento del Frontend.
    Payload esperado: { "type": "play", "data": { ... } }
    """
    # Intentar obtener usuario (si hay login)
    user = request.session.get("user")
    user_id = user['uid'] if user else "anonimo"

    servicio = AnalyticsService(session)
    return servicio.registrar_evento(user_id, payload.get("type"), payload.get("data", {}))


@router.get("/insights")
def get_user_insights(request: Request, session: Session = Depends(get_session)):
    user = request.session.get("user")
    user_id = user['uid'] if user else "anonimo"

    servicio = AnalyticsService(session)

    return {
        "explorador": servicio.analizar_explorador(user_id),
        "horario": servicio.analizar_horarios(user_id),
        "energia": servicio.comparar_energia(user_id)
    }