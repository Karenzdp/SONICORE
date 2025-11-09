from fastapi import APIRouter, HTTPException, Depends

from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from passlib.context import CryptContext
from models.usuario import Usuario, UsuarioCreate, UsuarioRead, UsuarioUpdate
from database.database import engine

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

# Configurar encriptación de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 🔹 Crear usuario
@router.post("/", response_model=UsuarioRead, status_code=201)
def crear_usuario(usuario: UsuarioCreate):
    with Session(engine) as session:
        if session.exec(select(Usuario).where(Usuario.nombre_usuario == usuario.nombre_usuario)).first():
            raise HTTPException(status_code=400, detail="Nombre de usuario ya registrado")
        if session.exec(select(Usuario).where(Usuario.correo == usuario.correo)).first():
            raise HTTPException(status_code=400, detail="Correo ya registrado")

        # Encriptar contraseña
        hashed_password = pwd_context.hash(usuario.contrasena)
        nuevo_usuario = Usuario(
            nombre_usuario=usuario.nombre_usuario,
            correo=usuario.correo,
            contrasena=hashed_password
        )

        session.add(nuevo_usuario)
        session.commit()
        session.refresh(nuevo_usuario)
        return nuevo_usuario



# 🔹 Obtener todos los usuarios
@router.get("/activos")
def obtener_usuarios_activos():
    with Session(engine) as session:
        usuarios_activos = session.exec(select(Usuario).where(Usuario.activo == True)).all()
        if not usuarios_activos:
            raise HTTPException(status_code=404, detail="No hay usuarios activos registrados")
        return usuarios_activos

@router.get("/inactivos")
def obtener_usuarios_inactivos():
    with Session(engine) as session:
        usuarios_inactivos = session.exec(select(Usuario).where(Usuario.activo == False)).all()
        if not usuarios_inactivos:
            raise HTTPException(status_code=404, detail="No hay usuarios inactivos registrados")
        return usuarios_inactivos

# 🔹 Obtener usuario por ID
@router.get("/{id_usuario}", response_model=UsuarioRead)
def obtener_usuario(id_usuario: int):
    with Session(engine) as session:
        usuario = session.get(Usuario, id_usuario)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return usuario

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    with Session(engine) as session:
        usuario = session.exec(
            select(Usuario).where(Usuario.nombre_usuario == form_data.username)
        ).first()

        if not usuario:
            raise HTTPException(status_code=400, detail="Usuario no encontrado")

        # Verificar contraseña
        if not pwd_context.verify(form_data.password, usuario.contrasena):
            raise HTTPException(status_code=400, detail="Contraseña incorrecta")

        return {"mensaje": "Inicio de sesión exitoso", "usuario": usuario.nombre_usuario}

# 🔹 Actualizar usuario
@router.put("/{id_usuario}")
def actualizar_usuario(id_usuario: int, usuario_actualizado: UsuarioUpdate):
    with Session(engine) as session:
        usuario_db = session.get(Usuario, id_usuario)
        if not usuario_db:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # Solo actualiza los campos que vienen con valor (no los vacíos o None)
        datos = usuario_actualizado.dict(exclude_unset=True)

        for campo, valor in datos.items():
            if valor not in ("", None):  # Evita sobreescribir con vacío
                setattr(usuario_db, campo, valor)

        session.add(usuario_db)
        session.commit()
        session.refresh(usuario_db)

        return {"mensaje": "Usuario actualizado correctamente", "usuario": usuario_db}

# 🔹 Eliminar (marcar inactivo)
@router.delete("/{id_usuario}")
def eliminar_usuario(id_usuario: int):
    with Session(engine) as session:
        usuario = session.get(Usuario, id_usuario)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        usuario.activo = False
        session.add(usuario)
        session.commit()
        return {"mensaje": "Usuario desactivado correctamente"}
