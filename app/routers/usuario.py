from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from app.dependencies import get_session
from app.repositories.usuario_repo import UsuarioRepository
from app.models.usuario import UsuarioRead, UsuarioCreate

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.post("/", response_model=UsuarioRead)
def registro(usuario: UsuarioCreate, session: Session = Depends(get_session)):
    repo = UsuarioRepository(session)
    return repo.registrar(usuario)

@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    repo = UsuarioRepository(session)
    user = repo.login(form.username, form.password)
    if not user:
        raise HTTPException(400, "Credenciales inválidas")
    return {"mensaje": "Login exitoso", "usuario": user.nombre_usuario}