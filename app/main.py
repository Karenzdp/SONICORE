from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from app.database import create_db_and_tables

# --- IMPORTACIÓN DE ROUTERS (ENDPOINTS) ---
from app.routers import (
    artistas,
    albumes,
    canciones,
    generos,
    usuario,
    web,
    reportes,
    spotify_full,
    player,
    apis,
    analytics
)

# --- IMPORTACIÓN DE SERVICIO (Para Callback) ---
from app.services.music_service import MusicService

# 1. CREACIÓN DE LA APP
app = FastAPI(
    title="SONICORE - Plataforma de Gestión Musical",
    description="API Profesional con integración de Spotify, Supabase y Analytics",
    version="3.0.0"
)

# 2. CONFIGURACIÓN DE SEGURIDAD (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 3. EVENTO DE INICIO (BASE DE DATOS)
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    print("✅ Base de datos sincronizada y lista.")


# 4. ARCHIVOS ESTÁTICOS (CSS, JS, IMÁGENES)
# Nota: La carpeta 'static' está en la raíz del proyecto, fuera de 'app'
app.mount("/static", StaticFiles(directory="static"), name="static")

# 5. REGISTRO DE RUTAS (INCLUSIÓN DE ROUTERS)
app.include_router(web.router)  # Frontend (HTML/Jinja2)
app.include_router(usuario.router)  # Login y Usuarios
app.include_router(reportes.router)  # 📊 Analytics (Dataset Kaggle)
app.include_router(artistas.router)  # 📸 Artistas (Supabase)
app.include_router(albumes.router)  # Álbumes
app.include_router(canciones.router)  # Canciones
app.include_router(generos.router)  # Géneros
app.include_router(player.router)  # Reproductor (Play/Pause)
app.include_router(spotify_full.router)  # API Spotify Completa
app.include_router(apis.router)  # Rutas adicionales
app.add_middleware(SessionMiddleware, secret_key="una-clave-super-secreta-y-segura")
app.include_router(analytics.router)

# 6. RUTA RAÍZ (REDIRECCIÓN)
@app.get("/")
def read_root():
    # Al entrar a la raíz, nos manda directo al Dashboard visual
    return RedirectResponse(url="/web/")


# 7. CALLBACK DE SPOTIFY (LOGIN)
@app.get("/callback")
def callback(code: str):
    """
    Recibe el código de autorización de Spotify, obtiene el token
    y lo guarda en una cookie del navegador.
    """
    try:
        service = MusicService()
        token_info = service.set_token(code)

        # Redirigimos al usuario de vuelta al Dashboard
        response = RedirectResponse(url="/web/")

        # Guardamos el token en una cookie para que el reproductor funcione
        response.set_cookie(key="spotify_token", value=token_info['access_token'])

        return response
    except Exception as e:
        return {"error": f"Error en autenticación con Spotify: {str(e)}"}