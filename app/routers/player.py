from fastapi import APIRouter, Request, HTTPException
from app.services.music_service import MusicService

router = APIRouter(prefix="/player", tags=["Player Control"])
service = MusicService() # Instancia sin sesión BD, solo para Spotify

def get_token(request: Request):
    # Recuperamos el token de la cookie (lo guardaremos en el login)
    token = request.cookies.get("spotify_token")
    if not token:
        raise HTTPException(status_code=401, detail="No conectado a Spotify")
    return token

@router.get("/current")
def current_playback(request: Request):
    token = get_token(request)
    return service.get_player_state(token)

@router.post("/play")
def play(request: Request):
    token = get_token(request)
    service.play(token)
    return {"status": "ok"}

@router.post("/pause")
def pause(request: Request):
    token = get_token(request)
    service.pause(token)
    return {"status": "ok"}

@router.post("/next")
def next_track(request: Request):
    token = get_token(request)
    service.next_track(token)
    return {"status": "ok"}

@router.post("/prev")
def prev_track(request: Request):
    token = get_token(request)
    service.previous_track(token)
    return {"status": "ok"}