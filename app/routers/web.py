from fastapi import APIRouter, Request, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from typing import Optional

# --- DEPENDENCIAS Y SERVICIOS ---
from app.dependencies import get_session
from app.services.music_service import MusicService
from app.services.analytics_service import AnalyticsService

# --- REPOSITORIOS ---
from app.repositories.artistas_repo import ArtistaRepository
from app.repositories.albumes_repo import AlbumRepository
from app.repositories.canciones_repo import CancionRepository
from app.repositories.generos_repo import GeneroRepository

from app.models.generos import Genero
# --- MODELOS ---
from app.models.favoritos import Favorito
from app.models.canciones import Cancion
from app.models.artistas import Artista
from app.models.albumes import Album
# 👇 IMPORTACIÓN CRÍTICA PARA EL DIAGNÓSTICO
from app.models.analytics import UserEvent

router = APIRouter(prefix="/web", tags=["Web Interface"])
templates = Jinja2Templates(directory="templates")


# ==============================================================================
# RUTA PRINCIPAL (DASHBOARD)
# ==============================================================================
@router.get("/")
async def dashboard(
        request: Request,
        filtro: str = "inicio",
        q: str = "",
        session: Session = Depends(get_session)
):
    """
    Controlador principal que renderiza el dashboard.
    Maneja: Autenticación, Búsqueda, Filtrado y Analíticas (Insights).
    """

    # 1. AUTENTICACIÓN Y SESIÓN
    # ---------------------------------------------------------
    user = request.session.get("user")

    # 2. DIAGNÓSTICO DE ANALYTICS (MODO FORENSE) - SOPORTE ANÓNIMO
    # ---------------------------------------------------------
    insights = None

    # Determinar user_id (autenticado o anónimo)
    user_id = user.get('uid') if user else "anonimo"

    print(f"\n{'=' * 40}")
    print(f"🕵️‍♂️ INICIO DIAGNÓSTICO DASHBOARD")
    print(f"👤 Usuario: {user.get('display_name') if user else 'Anónimo'} (ID: {user_id})")

    try:
        analytics = AnalyticsService(session)

        # Verificamos si realmente hay datos en la BD para este usuario
        eventos = session.exec(select(UserEvent).where(UserEvent.user_id == user_id)).all()
        total_eventos = len(eventos)

        print(f"📊 Eventos en Base de Datos: {total_eventos}")

        if total_eventos > 0:
            print(f"✅ Hay datos. Último evento detectado: {eventos[-1].event_type}")

            # Calculamos métricas
            energia = analytics.comparar_energia(user_id)
            explorador = analytics.analizar_explorador(user_id)
            horario = analytics.analizar_horarios(user_id)

            print(f"⚡ Insight Energía calculado: {energia}")

            raw_insights = {
                "energia": energia,
                "explorador": explorador,
                "horario": horario
            }

            # Filtros de visualización (Para no mostrar tarjetas vacías)
            has_energy = raw_insights.get('energia') is not None and raw_insights['energia'].get(
                'tu_energia') is not None
            has_explorer = raw_insights.get('explorador') and raw_insights['explorador']['score'] > 0

            if has_energy or has_explorer:
                insights = raw_insights
                print("🏆 Insights generados correctamente y enviados al template.")
            else:
                print(
                    "⚠️ Datos existen pero no generaron insights válidos (Falta 'energy' en el JSON o poca actividad).")
        else:
            print("❌ BASE DE DATOS DE EVENTOS VACÍA PARA ESTE USUARIO.")
            print("💡 Pista: El auto-generador JavaScript debería crear eventos automáticamente.")

    except Exception as e:
        print(f"🔥 EXCEPCIÓN CRÍTICA EN ANALYTICS: {e}")
        import traceback
        traceback.print_exc()
        insights = None
    print(f"{'=' * 40}\n")

    # 3. INICIALIZACIÓN DE REPOSITORIOS
    # ---------------------------------------------------------
    repo_artista = ArtistaRepository(session)
    repo_album = AlbumRepository(session)
    repo_cancion = CancionRepository(session)
    repo_genero = GeneroRepository(session)

    # Contexto base para pasar a la plantilla HTML
    context = {
        "request": request,
        "filtro_actual": filtro,
        "usuario": user['display_name'] if user else None,
        "busqueda": q,
        "insights": insights,  # <--- Aquí viajan los datos a la tarjeta roja

        # Inicializamos listas vacías para evitar errores en Jinja2
        "mis_artistas": [],
        "favoritos": [],
        "generos": [],
        "artistas": [],
        "albumes": [],
        "canciones": [],
        "playlists": [],
        "mis_likes": []
    }

    # 4. LÓGICA DE BÚSQUEDA O NAVEGACIÓN
    # ---------------------------------------------------------
    if q:
        # --- CASO A: EL USUARIO ESTÁ BUSCANDO ---
        print(f"🔍 Buscando: {q}")
        context["artistas"] = repo_artista.buscar_por_nombre(q)

        # Búsqueda manual en álbumes (si el repo no tiene método específico)
        all_albs = repo_album.get_all()
        context["albumes"] = [a for a in all_albs if q.lower() in a.nombre.lower()]

        # Búsqueda manual en canciones
        all_cans = repo_cancion.get_all()
        context["canciones"] = [c for c in all_cans if q.lower() in c.titulo.lower()]

    else:
        # --- CASO B: NAVEGACIÓN POR PESTAÑAS (SIDEBAR) ---

        if filtro == "inicio":
            # Cargar resumen para el Home
            context["mis_artistas"] = repo_artista.get_all()[:10]  # Simulando 'Mis Artistas'

            # Cargar Favoritos (Likes)
            try:
                ids_favs = session.exec(select(Favorito.cancion_id)).all()
                if ids_favs:
                    context["favoritos"] = session.exec(select(Cancion).where(Cancion.id_cancion.in_(ids_favs))).all()
            except Exception as e:
                print(f"Error cargando favoritos: {e}")

            context["generos"] = repo_genero.get_all()

        elif filtro == "artistas":
            context["artistas"] = repo_artista.get_all()

        elif filtro == "albunes":
            context["albumes"] = repo_album.get_all()

        elif filtro == "canciones":
            context["canciones"] = repo_cancion.get_all()
            # Cargar lista de IDs likeados para pintar los corazones
            try:
                context["mis_likes"] = session.exec(select(Favorito.cancion_id)).all()
            except:
                context["mis_likes"] = []

        elif filtro == "generos":
            context["generos"] = repo_genero.get_all()

    # DEBUG: Verificar insights
    if context.get("insights"):
        print(f"✅ INSIGHTS EN CONTEXTO: {context['insights']}")
    else:
        print("❌ NO HAY INSIGHTS EN CONTEXTO")

    return templates.TemplateResponse("dashboard.html", context)



# ==============================================================================
# RUTAS AUXILIARES PARA EL FRONTEND (AJAX / FETCH)
# ==============================================================================

@router.get("/sugerencias")
def sugerencias(q: str, session: Session = Depends(get_session)):
    """Endpoint ligero para el autocompletado de la barra de búsqueda"""
    if not q: return []

    repo_art = ArtistaRepository(session)
    repo_can = CancionRepository(session)

    resultados = []

    # 1. Buscar artistas
    arts = repo_art.buscar_por_nombre(q)
    for a in arts[:3]:
        resultados.append({"nombre": a.nombre, "tipo": "Artista", "id": a.id_artista})

    # 2. Buscar canciones
    all_cans = repo_can.get_all()
    cans = [c for c in all_cans if q.lower() in c.titulo.lower()][:3]
    for c in cans:
        resultados.append({"nombre": c.titulo, "tipo": "Canción", "id": c.id_cancion})

    return resultados


# ============================================================================
# API PARA EL FRONTEND (DENTRO DE web_router.py)
# ============================================================================

@router.get("/api/song_data/{id_cancion}")
def get_song_data(id_cancion: int, session: Session = Depends(get_session)):
    """API para obtener datos enriquecidos de una canción"""
    try:
        cancion = session.get(Cancion, id_cancion)
        if not cancion:
            raise HTTPException(status_code=404, detail="Canción no encontrada")

        # Cargar relaciones
        artista = session.get(Artista, cancion.artista_id) if cancion.artista_id else None
        album = session.get(Album, cancion.album_id) if cancion.album_id else None
        genero = session.get(Genero, cancion.genero_id) if cancion.genero_id else None

        # Determinar foto
        foto = None
        if album and hasattr(album, 'foto_portada') and album.foto_portada:
            foto = album.foto_portada
        elif artista and hasattr(artista, 'foto') and artista.foto:
            foto = artista.foto

        return {
            "id": cancion.id_cancion,
            "titulo": cancion.titulo,
            "duracion": cancion.duracion,
            "anio": cancion.anio_lanzamiento,  # ⚠️ MAPEO CORRECTO
            "artista_id": cancion.artista_id,
            "artista_nombre": artista.nombre if artista else "Desconocido",
            "album_id": cancion.album_id,
            "album_nombre": album.nombre if album else "Sencillo / Sin Álbum",
            "genero_id": cancion.genero_id,
            "genero_nombre": genero.nombre if genero else "General",
            "foto": foto
        }

    except HTTPException:
        raise

    except Exception as e:
        print(f"🔥 ERROR en get_song_data: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error interno: {str(e)}"
        )
@router.post("/like/{id_cancion}")
def toggle_like(id_cancion: int, request: Request, session: Session = Depends(get_session)):
    """Maneja el Like/Dislike de canciones locales"""
    user = request.session.get("user")
    if not user:
        return {"error": "Debes iniciar sesión"}

    # Verificar si ya existe el like
    existing = session.exec(select(Favorito).where(
        Favorito.cancion_id == id_cancion
        # Favorito.user_id == user['uid'] # Descomentar si implementas likes por usuario
    )).first()

    if existing:
        session.delete(existing)
        session.commit()
        return {"es_favorito": False}
    else:
        nuevo = Favorito(cancion_id=id_cancion)
        session.add(nuevo)
        session.commit()
        return {"es_favorito": True}


@router.get("/analisis/{spotify_id}")
def analisis_track(spotify_id: str, request: Request, session: Session = Depends(get_session)):
    """Proxy hacia Spotify para obtener Audio Features (Energy, Tempo, etc.)"""
    ms = MusicService(session)
    token = request.session.get("token_info", {}).get("access_token")
    return ms.obtener_analisis_audio(spotify_id, user_token=token)


@router.get("/spotify_search_track")
def search_track_spotify(q: str, session: Session = Depends(get_session)):
    """Helper para buscar el ID de Spotify de una canción local"""
    ms = MusicService(session)
    return ms.search(q, type='track', limit=1)


# ==============================================================================
# RUTAS DE ACCESO
# ==============================================================================
@router.get("/login")
def login_page():
    return RedirectResponse("/spotify/login")


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/web/?filtro=inicio")


@router.get("/api/album_data/{id_album}")
def get_album_data(id_album: int, session: Session = Depends(get_session)):
    """API para obtener datos completos de un álbum para el Modal"""
    repo_alb = AlbumRepository(session)
    album = repo_alb.get_by_id(id_album)
    if not album: return {"error": "Álbum no encontrado"}

    # Obtener nombre del artista
    repo_art = ArtistaRepository(session)
    artista = repo_art.get_by_id(album.artista_principal_id)
    artista_nombre = artista.nombre if artista else "Desconocido"

    # Obtener canciones
    canciones = session.exec(select(Cancion).where(Cancion.album_id == id_album)).all()

    return {
        "id": album.id_album,
        "nombre": album.nombre,
        "anio": album.anio_lanzamiento,
        "foto": album.foto_portada,
        "descripcion": album.descripcion,
        "artista_id": album.artista_principal_id,
        "artista_nombre": artista_nombre,
        "genero_id": album.genero_id,
        "canciones": [{"id": c.id_cancion, "titulo": c.titulo, "duracion": c.duracion} for c in canciones]
    }


# ==============================================================================
# BÚSQUEDA EN SPOTIFY (CUANDO NO HAY RESULTADOS LOCALES)
# ==============================================================================
@router.get("/buscar-spotify")
def buscar_spotify(q: str, session: Session = Depends(get_session)):
    """
    Busca en Spotify API y retorna resultados formateados.
    Se llama desde el frontend cuando la búsqueda local no da resultados.
    """
    if not q or len(q.strip()) < 2:
        return {"artistas": [], "albumes": [], "canciones": []}

    ms = MusicService(session)

    try:
        # Buscar en Spotify (artistas, álbumes, canciones)
        resultados = ms.search(q, type='track,artist,album', limit=5)

        # Formatear artistas
        artistas_spotify = []
        if 'artists' in resultados and resultados['artists']['items']:
            for item in resultados['artists']['items']:
                artistas_spotify.append({
                    "id": item['id'],
                    "nombre": item['name'],
                    "foto": item['images'][0]['url'] if item.get('images') else None,
                    "tipo": "spotify_artist"
                })

        # Formatear álbumes
        albumes_spotify = []
        if 'albums' in resultados and resultados['albums']['items']:
            for item in resultados['albums']['items']:
                albumes_spotify.append({
                    "id": item['id'],
                    "nombre": item['name'],
                    "foto": item['images'][0]['url'] if item.get('images') else None,
                    "artista": item['artists'][0]['name'] if item.get('artists') else "Desconocido",
                    "anio": item['release_date'][:4] if item.get('release_date') else "",
                    "tipo": "spotify_album"
                })

        # Formatear canciones
        canciones_spotify = []
        if 'tracks' in resultados and resultados['tracks']['items']:
            for item in resultados['tracks']['items']:
                ms_dur = item['duration_ms']
                duracion = f"{int(ms_dur / 60000)}:{int((ms_dur % 60000) / 1000):02d}"

                canciones_spotify.append({
                    "id": item['id'],
                    "titulo": item['name'],
                    "artista": item['artists'][0]['name'] if item.get('artists') else "Desconocido",
                    "duracion": duracion,
                    "foto": item['album']['images'][0]['url'] if item['album'].get('images') else None,
                    "tipo": "spotify_track"
                })

        return {
            "artistas": artistas_spotify,
            "albumes": albumes_spotify,
            "canciones": canciones_spotify
        }

    except Exception as e:
        print(f"❌ Error buscando en Spotify: {e}")
        return {"artistas": [], "albumes": [], "canciones": [], "error": str(e)}


@router.post("/importar-desde-spotify")
def importar_desde_spotify(
        spotify_id: str = Query(...),
        tipo: str = Query(...),
        session: Session = Depends(get_session)
):
    ms = MusicService(session)

    try:
        resultado = ms.importar_inteligente(spotify_id, tipo)
        session.commit()  # ⚠️ AGREGA ESTO
        session.close()  # ⚠️ Y ESTO
        return resultado
    except Exception as e:
        session.rollback()
        return {"error": str(e)}
    
@router.get("/api/artist_data/{id_artista}")
def get_artist_data(id_artista: int, session: Session = Depends(get_session)):
    """API para obtener datos completos de un artista para el Modal Glass"""
    repo = ArtistaRepository(session)
    artista = repo.get_by_id(id_artista)
    if not artista:
        return {"error": "Artista no encontrado"}
    
    # Estructura de respuesta enriquecida
    resp = {
        "id": artista.id_artista, 
        "nombre": artista.nombre, 
        "nacionalidad": artista.nacionalidad,
        "biografia": artista.biografia, 
        "foto": artista.foto, 
        "albumes": [], 
        "canciones": []
    }
    
    try:
        # Cargar Álbumes
        from app.models.albumes import Album
        albs = session.exec(select(Album).where(Album.artista_principal_id == id_artista)).all()
        for a in albs: 
            resp["albumes"].append({
                "id": a.id_album, 
                "nombre": a.nombre, 
                "anio": a.anio_lanzamiento, 
                "foto": a.foto_portada
            })
            
        # Cargar Canciones Top (Las que no pertenecen a un álbum específico o todas)
        # Nota: Aquí mostramos todas las del artista limitadas a 10 para el perfil
        from app.models.canciones import Cancion
        cans = session.exec(select(Cancion).where(Cancion.artista_id == id_artista).limit(10)).all()
        for c in cans: 
            resp["canciones"].append({
                "id": c.id_cancion, 
                "titulo": c.titulo, 
                "duracion": c.duracion, 
                "album_id": c.album_id
            })
    except Exception as e:
        print(f"⚠️ Error cargando relaciones artista: {e}")

    return resp