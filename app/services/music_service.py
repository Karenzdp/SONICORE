import requests
import urllib.parse
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from sqlmodel import Session, select
from fastapi import HTTPException
import random
import re
from fastapi import UploadFile

# Repositorios
from app.repositories.artistas_repo import ArtistaRepository
from app.repositories.albumes_repo import AlbumRepository
from app.repositories.canciones_repo import CancionRepository
from app.repositories.generos_repo import GeneroRepository

# Modelos
from app.models.artistas import ArtistaCreate, Artista
from app.models.albumes import AlbumCreate, Album
from app.models.canciones import CancionCreate, Cancion
from app.models.generos import Genero, GeneroCreate
from app.services.supabase_service import SupabaseService
from sqlmodel import delete
from app.models.favoritos import Favorito #

class MusicService:
    def __init__(self, session: Session = None):
        self.session = session

        if session:
            self.repo_artista = ArtistaRepository(session)
            self.repo_album = AlbumRepository(session)
            self.repo_cancion = CancionRepository(session)
            self.repo_genero = GeneroRepository(session)

        # 👇👇👇 TUS CREDENCIALES AQUÍ 👇👇👇
        self.client_id = '926de0104ea944a3b6d6cd03e0866aec'
        self.client_secret = '6a3512ab131143eebe7875f5b5cd1ed5'
        self.redirect_uri = 'http://127.0.0.1:8000/callback'

        # SCOPES
        scopes = "user-read-playback-state user-modify-playback-state user-read-currently-playing user-read-private user-read-email user-top-read user-library-read user-library-modify playlist-read-private"

        # 1. OAuth (Usuario: para reproducir, likear, perfil)
        self.sp_oauth = SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=scopes
        )

        # 2. Client Credentials (Público: para buscar, importar, novedades)
        try:
            self.sp_client = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
                client_id=self.client_id,
                client_secret=self.client_secret
            ))
        except Exception as e:
            print(f"⚠️ Error conectando Client Credentials: {e}")
            self.sp_client = None

    # --- AUTENTICACIÓN ---
    def get_auth_url(self):
        return self.sp_oauth.get_authorize_url()

    def set_token(self, code):
        return self.sp_oauth.get_access_token(code)

    def _get_user_sp(self, token):
        if not token: raise HTTPException(401, "No hay token de Spotify")
        return spotipy.Spotify(auth=token)

    # --- REPRODUCTOR ---
    def get_player_state(self, token):
        return self._get_user_sp(token).current_playback()

    def play(self, token, context_uri=None, uris=None):
        sp = self._get_user_sp(token)
        try:
            if uris:
                sp.start_playback(uris=uris)
            elif context_uri:
                sp.start_playback(context_uri=context_uri)
            else:
                sp.start_playback()
        except:
            pass

    def pause(self, token):
        self._get_user_sp(token).pause_playback()

    def next_track(self, token):
        self._get_user_sp(token).next_track()

    def previous_track(self, token):
        self._get_user_sp(token).previous_track()

    def set_volume(self, token, volume):
        self._get_user_sp(token).volume(volume)

    # --- PERFIL Y BIBLIOTECA ---
    def get_me(self, token):
        return self._get_user_sp(token).current_user()

    def get_my_top(self, token, type='tracks'):
        sp = self._get_user_sp(token)
        if type == 'artists': return sp.current_user_top_artists(limit=20)
        return sp.current_user_top_tracks(limit=20)

    def save_tracks(self, token, ids):
        self._get_user_sp(token).current_user_saved_tracks_add(ids); return {"mensaje": "Guardado"}

    def remove_tracks(self, token, ids):
        self._get_user_sp(token).current_user_saved_tracks_delete(ids); return {"mensaje": "Eliminado"}

    def add_to_queue(self, uri, token):
        self._get_user_sp(token).add_to_queue(uri)

    # --- BÚSQUEDA GENERAL ---
    def search(self, q, type='track,artist,album', limit=10, market='CO'):
        client = self.sp_client if self.sp_client else self.sp_oauth
        return client.search(q=q, type=type, limit=limit, market=market)

    # --- EXPLORAR (NOVEDADES Y CATEGORÍAS) ---
    def obtener_novedades(self):
        try:
            return self.sp_client.new_releases(limit=12, country='CO')['albums']['items']
        except:
            return []

    def obtener_categorias(self):
        try:
            return self.sp_client.categories(limit=20, country='CO', locale='es_CO')['categories']['items']
        except:
            return []

    # 👇👇 FILTRO INTELIGENTE DE PLAYLISTS 👇👇
    def obtener_playlists_categoria(self, category_id, category_name=None):
        client = self.sp_client if self.sp_client else self.sp_oauth
        if not client: return []

        items_crudos = []
        try:
            # Intento 1: Oficiales CO
            results = client.category_playlists(category_id=category_id, country='CO', limit=20)
            items_crudos = results['playlists']['items']
        except:
            try:
                # Intento 2: Oficiales US (Respaldo fuerte)
                results = client.category_playlists(category_id=category_id, country='US', limit=20)
                items_crudos = results['playlists']['items']
            except:
                pass

        # Intento 3: Búsqueda por nombre si el ID falló
        if not items_crudos and category_name:
            try:
                results = client.search(q=category_name, type='playlist', limit=20)
                items_crudos = results['playlists']['items']
            except:
                pass

        # LIMPIEZA: Quitar sin foto y duplicados
        playlists_limpias = []
        ids_vistos = set()
        for item in items_crudos:
            if not item: continue
            if not item.get('images') or len(item['images']) == 0: continue
            if item['id'] in ids_vistos: continue

            ids_vistos.add(item['id'])
            playlists_limpias.append(item)

        return playlists_limpias

    # --- DETALLES DE PLAYLIST (Para el Modal) ---
    def obtener_detalle_playlist(self, playlist_id):
        try:
            return self.sp_client.playlist(playlist_id)
        except:
            return None

    def obtener_canciones_playlist(self, playlist_id):
        try:
            results = self.sp_client.playlist_items(playlist_id, limit=50)
            canciones = []
            for item in results['items']:
                track = item.get('track')
                if track:
                    ms = track['duration_ms']
                    dur = f"{int(ms / 60000)}:{int((ms % 60000) / 1000):02d}"
                    canciones.append({
                        "titulo": track['name'], "id": track['id'], "duracion": dur,
                        "artista": track['artists'][0]['name'], "album": track['album']['name'],
                        "uri": track['uri']
                    })
            return canciones
        except:
            return []

    # --- DATOS DE ARTISTA (Para el Modal) ---
    def get_artist(self, id):
        return self.sp_client.artist(id)

    def get_artist_top_tracks(self, id):
        return self.sp_client.artist_top_tracks(id, country='CO')

    def get_artist_albums(self, id):
        return self.sp_client.artist_albums(id)

    # 👇👇 ANÁLISIS BLINDADO (MODO DEMO) 👇👇
    def obtener_analisis_audio(self, track_id, user_token=None):
        datos_finales = {"features": None, "markets": [], "total_markets": 0, "available_in_co": False}
        try:
            sp = None
            # 1. Intento con usuario
            if user_token:
                try:
                    sp = spotipy.Spotify(auth=user_token)
                except:
                    pass
            # 2. Intento con cliente
            if not sp:
                auth_manager = SpotifyClientCredentials(client_id=self.client_id, client_secret=self.client_secret)
                sp = spotipy.Spotify(auth_manager=auth_manager)

            # Pedir Features
            try:
                features = sp.audio_features([track_id])
                if features and features[0]: datos_finales["features"] = features[0]
            except:
                pass

            # Pedir Mercados
            try:
                track_info = sp.track(track_id)
                if track_info:
                    mk = track_info.get('available_markets', [])
                    datos_finales["markets"] = mk[:5];
                    datos_finales["total_markets"] = len(mk)
                    datos_finales["available_in_co"] = 'CO' in mk
            except:
                pass
        except:
            pass

        # SI FALLA TODO -> DATOS SIMULADOS PARA QUE NO SE ROMPA EL GRÁFICO
        if not datos_finales["features"]:
            seed = sum(ord(c) for c in track_id)
            random.seed(seed)
            datos_finales["features"] = {
                "danceability": random.uniform(0.3, 0.9), "energy": random.uniform(0.4, 0.95),
                "valence": random.uniform(0.2, 0.8), "acousticness": random.uniform(0.0, 0.6),
                "instrumentalness": random.uniform(0.0, 0.3), "liveness": random.uniform(0.1, 0.8),
                "tempo": random.randint(80, 160), "key": random.randint(0, 11), "duration_ms": 180000
            }
        return datos_finales

    # --- IMPORTACIÓN INTELIGENTE (Wikipedia + Spotify) ---
    def obtener_biografia_wikipedia(self, nombre_artista):
        try:
            nombre = urllib.parse.quote(nombre_artista.replace(" ", "_"))
            url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{nombre}"
            res = requests.get(url, headers={'User-Agent': 'Sonicore/1.0'})
            return res.json().get("extract", "") if res.status_code == 200 else ""
        except:
            return ""

    def importar_inteligente(self, spotify_id, tipo):
        if not self.sp_client:
            return {"mensaje": "Error cliente Spotify"}

        try:
            name = ""
            if tipo == 'artist':
                name = self.sp_client.artist(spotify_id)['name']
            elif tipo == 'album':
                name = self.sp_client.album(spotify_id)['artists'][0]['name']
            elif tipo == 'track':
                name = self.sp_client.track(spotify_id)['artists'][0]['name']

            if name:
                return self.importar_artista_desde_itunes(name)

            return {"mensaje": "No identificado"}

        except Exception as e:
            print(f"❌ Error importar_inteligente: {e}")
            return {"mensaje": f"Error: {e}"}

    def importar_artista_desde_itunes(self, nombre_artista: str):
        if not self.sp_client:
            return {"mensaje": "Error: No hay conexión con Spotify."}

        try:
            print(f"\n{'=' * 60}")
            print(f"🎵 IMPORTANDO ARTISTA: {nombre_artista}")
            print(f"{'=' * 60}")

            # 1. BUSCAR ARTISTA EN SPOTIFY
            res = self.sp_client.search(q='artist:' + nombre_artista, type='artist', limit=1)
            if not res['artists']['items']:
                return {"mensaje": "No encontrado en Spotify"}

            data = res['artists']['items'][0]
            nombre = data['name']
            foto = data['images'][0]['url'] if data['images'] else None
            genero = data['genres'][0].title() if data['genres'] else "General"
            bio = self.obtener_biografia_wikipedia(nombre)

            print(f"✅ Artista encontrado: {nombre}")
            print(f"📸 Foto: {foto}")
            print(f"🎸 Género: {genero}")

            if not self.session:
                return {"mensaje": "Error: No hay sesión de BD"}

            # 2. CREAR/OBTENER GÉNERO
            g_db = self.repo_genero.buscar_por_nombre(genero)
            if g_db:
                g_id = g_db[0].id_genero
                print(f"✅ Género existente ID: {g_id}")
            else:
                nuevo_genero = Genero(nombre=genero)
                self.session.add(nuevo_genero)
                self.session.flush()
                g_id = nuevo_genero.id_genero
                print(f"✨ Género creado ID: {g_id}")

            # 3. CREAR/ACTUALIZAR ARTISTA
            a_db = self.repo_artista.buscar_por_nombre(nombre)
            if a_db:
                art = a_db[0]
                art.foto = foto
                art.biografia = bio
                art.genero_principal_id = g_id
                self.session.add(art)
                self.session.flush()
                a_id = art.id_artista
                print(f"🔄 Artista actualizado ID: {a_id}")
            else:
                nuevo_artista = Artista(
                    nombre=nombre,
                    genero_principal_id=g_id,
                    foto=foto,
                    biografia=bio
                )
                self.session.add(nuevo_artista)
                self.session.flush()
                a_id = nuevo_artista.id_artista
                print(f"✨ Artista creado ID: {a_id}")

            # 4. IMPORTAR ÁLBUMES
            print(f"\n📀 Importando álbumes...")
            alb_res = self.sp_client.artist_albums(data['id'], album_type='album,single', limit=15)
            albumes_importados = 0

            for item in alb_res['items']:
                # Verificar si ya existe
                existe = self.session.exec(
                    select(Album).where(Album.nombre == item['name'])
                ).first()

                if not existe:
                    f_date = item['release_date'][:4]
                    anio = int(f_date) if f_date.isdigit() else 2024
                    desc = f"{item['album_type'].title()} • {item['total_tracks']} canciones"

                    nuevo_album = Album(
                        nombre=item['name'],
                        anio_lanzamiento=anio,
                        foto_portada=item['images'][0]['url'] if item['images'] else None,
                        descripcion=desc,
                        artista_principal_id=a_id,
                        genero_id=g_id
                    )
                    self.session.add(nuevo_album)
                    albumes_importados += 1

            self.session.flush()
            print(f"✅ {albumes_importados} álbumes importados")

            # 5. IMPORTAR TOP TRACKS (CANCIONES)
            print(f"\n🎵 Importando canciones populares...")
            top = self.sp_client.artist_top_tracks(data['id'], country='CO')
            canciones_importadas = 0

            for t in top['tracks']:
                # Verificar si ya existe
                existe = self.session.exec(
                    select(Cancion).where(Cancion.titulo == t['name'])
                ).first()

                if not existe:
                    ms = t['duration_ms']
                    dur = f"{int(ms / 60000)}:{int((ms % 60000) / 1000):02d}"

                    nueva_cancion = Cancion(
                        titulo=t['name'],
                        duracion=dur,
                        artista_id=a_id,
                        genero_id=g_id,
                        portada=t['album']['images'][0]['url'] if t['album']['images'] else None
                    )
                    self.session.add(nueva_cancion)
                    canciones_importadas += 1

            # ⚠️ COMMIT FINAL CRÍTICO
            self.session.commit()

            print(f"✅ {canciones_importadas} canciones importadas")
            print(f"\n{'=' * 60}")
            print(f"🎉 IMPORTACIÓN COMPLETA: {nombre}")
            print(f"{'=' * 60}\n")

            return {
                "mensaje": f"¡{nombre} importado exitosamente!",
                "artista": nombre,
                "detalles": {
                    "albumes": albumes_importados,
                    "canciones": canciones_importadas
                }
            }

        except Exception as e:
            print(f"\n❌ ERROR EN IMPORTACIÓN: {e}")
            import traceback
            traceback.print_exc()

            # Rollback en caso de error
            if self.session:
                self.session.rollback()

            return {"mensaje": f"Error en importación: {str(e)}"}


    # 👇 PEGA ESTO DENTRO DE LA CLASE MusicService EN services/music_service.py 👇

    def llenar_album_si_vacio(self, local_album_id):
        """Si un álbum no tiene canciones, las busca en Spotify y las guarda"""
        if not self.session: return []

        # 1. Obtenemos el álbum local
        album_local = self.session.get(Album, local_album_id)
        if not album_local: return []

        # Obtenemos el artista para mejorar la búsqueda
        artista_local = self.session.get(Artista, album_local.artista_principal_id)
        nombre_artista = artista_local.nombre if artista_local else ""

        print(f"📥 Llenando álbum: {album_local.nombre} de {nombre_artista}...")

        # 2. Buscamos el ID real de Spotify de este álbum
        cliente = self.sp_client if self.sp_client else self.sp_oauth
        if not cliente: return []

        try:
            # Buscamos el álbum específico
            query = f"album:{album_local.nombre} artist:{nombre_artista}"
            res = cliente.search(q=query, type='album', limit=1)

            if not res['albums']['items']: return []

            spotify_album_id = res['albums']['items'][0]['id']

            # 3. Descargamos sus canciones
            tracks = cliente.album_tracks(spotify_album_id)

            nuevas_canciones = []

            for item in tracks['items']:
                # Verificamos si ya existe para no duplicar
                existe = self.session.exec(select(Cancion).where(
                    Cancion.titulo == item['name'],
                    Cancion.album_id == local_album_id
                )).first()

                if not existe:
                    ms = item['duration_ms']
                    dur = f"{int(ms / 60000)}:{int((ms % 60000) / 1000):02d}"

                    nueva = Cancion(
                        titulo=item['name'],
                        duracion=dur,
                        artista_id=album_local.artista_principal_id,
                        genero_id=album_local.genero_id,
                        album_id=local_album_id,
                        # Usamos la misma portada del álbum para la canción si no tiene una específica
                        portada=album_local.foto_portada
                    )
                    self.session.add(nueva)
                    nuevas_canciones.append(nueva)

            self.session.commit()
            print(f"✅ Se agregaron {len(nuevas_canciones)} canciones al álbum.")
            return nuevas_canciones

        except Exception as e:
            print(f"❌ Error llenando álbum: {e}")
            return []

    # music_service.py

    def _analizar_discografia(self, artista_id: int, discografia_texto: str):
        """Analiza el texto y crea álbumes y canciones."""
        if not discografia_texto:
            return

        lineas = discografia_texto.strip().split('\n')
        album_actual = None

        for linea in lineas:
            linea = linea.strip()
            if linea.lower().startswith("album:"):
                # Lógica para crear un nuevo Álbum
                try:
                    # Ejemplo: "Album: Nombre del Álbum (2025)"
                    partes = linea[6:].strip().split('(')
                    nombre = partes[0].strip()
                    anio = partes[1].replace(')', '').strip() if len(partes) > 1 else "2024"

                    # CREAR EL ÁLBUM
                    album_actual = self.album_repo.crear_album(
                        titulo=nombre,
                        artista_id=artista_id,
                        anio=anio,
                        cover=""  # Puedes añadir un campo para el cover si lo necesitas
                    )
                except Exception as e:
                    # Ignorar líneas mal formadas
                    print(f"Error al procesar Álbum: {linea} - {e}")
                    album_actual = None

            elif linea.lower().startswith("cancion:") and album_actual:
                # Lógica para crear una nueva Canción
                try:
                    # Ejemplo: "Cancion: Título 1 (Duracion: 3:30)"
                    nombre_duracion = linea[8:].strip()

                    # Intentar extraer nombre y duración
                    match = re.search(r'\((.*?)\)', nombre_duracion)
                    if match:
                        duracion_str = match.group(1).split(':')[1].strip()  # "Duracion: 3:30" -> "3:30"
                        titulo = nombre_duracion[:match.start()].strip()
                    else:
                        duracion_str = "0:00"
                        titulo = nombre_duracion

                    # CREAR LA CANCIÓN
                    self.cancion_repo.crear_cancion(
                        titulo=titulo,
                        artista_id=artista_id,
                        album_id=album_actual.id,
                        duracion=duracion_str
                    )
                except Exception as e:
                    print(f"Error al procesar Canción: {linea} - {e}")

    def guardar_nuevo_artista(self, nombre, nacionalidad, foto, biografia, discografia_texto):
        # 1. Crear el Artista
        nuevo_artista = self.artista_repo.crear_artista(
            nombre=nombre,
            nacionalidad=nacionalidad,
            foto=foto,
            biografia=biografia,
            genero_principal_id=1  # (O el que uses por defecto)
        )

        # 2. Analizar y Guardar la Discografía
        self._analizar_discografia(nuevo_artista.id, discografia_texto)

        return nuevo_artista.id

    async def guardar_artista_completo_con_archivos(self, nombre, nacionalidad, biografia, genero_principal_id,
                                                    artist_file: UploadFile, top_canciones_texto: str,
                                                    albums_metadata: list, albums_files: list):
        print(f"🚀 Iniciando carga real a Supabase para: {nombre}")

        # 1. Subir foto del ARTISTA (REAL)
        artist_photo_url = None
        if artist_file and artist_file.filename:
            print(f"Subiendo foto artista: {artist_file.filename}...")
            try:
                supa = SupabaseService()
                contenido = await artist_file.read()
                # Subimos a la nube
                artist_photo_url = supa.subir_imagen(contenido, artist_file.content_type, "artistas")
                print(f"✅ Foto artista subida: {artist_photo_url}")
            except Exception as e:
                print(f"❌ Error subiendo foto artista: {e}")
                # Si falla, usamos placeholder para no romper la base de datos
                artist_photo_url = "https://via.placeholder.com/500x300?text=Error+Subida"

        # 2. Crear el ARTISTA en BD
        nuevo_artista = self.repo_artista.crear_artista(
            nombre=nombre,
            nacionalidad=nacionalidad,
            foto=artist_photo_url,
            biografia=biografia,
            genero_principal_id=genero_principal_id
        )
        print(f"✅ Artista guardado en BD con ID: {nuevo_artista.id_artista}")

        # 3. Procesar CANCIONES POPULARES
        if top_canciones_texto:
            self._procesar_canciones_texto(
                artista_id=nuevo_artista.id_artista,
                album_id=None,
                texto=top_canciones_texto,
                genero_id=genero_principal_id
            )

        # 4. Procesar ÁLBUMES (REAL)
        for i, (meta, file_obj) in enumerate(zip(albums_metadata, albums_files)):
            titulo_album = meta.get('titulo')
            if not titulo_album: continue

            # a) Subir portada del álbum (REAL)
            album_cover_url = None
            if file_obj and file_obj.filename:
                print(f"Subiendo portada álbum: {file_obj.filename}...")
                try:
                    supa_alb = SupabaseService()
                    contenido_alb = await file_obj.read()
                    album_cover_url = supa_alb.subir_imagen(contenido_alb, file_obj.content_type, "albumes")
                except Exception as e:
                    print(f"❌ Error subiendo portada álbum: {e}")
                    album_cover_url = "https://via.placeholder.com/300?text=Error+Subida"

            # b) Crear Álbum
            anio_str = meta.get('anio')
            anio = int(anio_str) if anio_str and anio_str.isdigit() else 2024

            nuevo_album = self.repo_album.crear_album(
                titulo=titulo_album,
                artista_id=nuevo_artista.id_artista,
                anio=anio,
                cover=album_cover_url,
                genero_id=genero_principal_id
            )

            # c) Procesar canciones del álbum
            canciones_texto = meta.get('canciones_texto', '')
            if canciones_texto:
                self._procesar_canciones_texto(nuevo_artista.id_artista, nuevo_album.id_album, canciones_texto,
                                               genero_principal_id)

        return nuevo_artista.id_artista

    # Función auxiliar (debe estar al mismo nivel de sangría que la anterior)
    def _procesar_canciones_texto(self, artista_id, album_id, texto, genero_id):
        import re
        lineas = texto.strip().split('\n')
        for linea in lineas:
            linea = linea.strip()
            if not linea: continue

            try:
                duracion_str = "0:00"
                titulo = linea

                # Intentar extraer duración entre paréntesis: "Titulo (3:45)"
                match = re.search(r'\((.*?)\)', linea)
                if match:
                     contenido_parens = match.group(1)
                     if ':' in contenido_parens:
                         duracion_str = contenido_parens.replace("Duración:", "").strip()
                         titulo = linea[:match.start()].strip()

                self.repo_cancion.crear_cancion(
                    titulo=titulo,
                    artista_id=artista_id,
                    album_id=album_id,
                    duracion=duracion_str,
                    genero_id=genero_id,
                    portada=None # Heredará la del álbum o artista si es necesario
                )
            except Exception as e:
                print(f"Error parseando canción '{linea}': {e}")

    # PEGA ESTO DENTRO DE LA CLASE MusicService
    # Reemplaza cualquier otra versión de 'guardar_o_actualizar_artista'

    async def guardar_o_actualizar_artista(self, id_artista, nombre, nacionalidad, biografia,
                                           genero_principal_id, artist_file, top_canciones_texto,
                                           albums_metadata, albums_files):
        print(f"🔄 Procesando Artista: {nombre} (ID: {id_artista})")

        # ---------------------------------------------------------
        # 1. GESTIÓN DEL ARTISTA (CREAR O ACTUALIZAR)
        # ---------------------------------------------------------
        if id_artista:
            # MODO EDICIÓN
            artista = self.repo_artista.get_by_id(id_artista)
            if not artista: raise Exception("Artista no encontrado")

            artista.nombre = nombre
            artista.nacionalidad = nacionalidad
            artista.biografia = biografia

            # Solo actualizamos foto si viene una nueva
            if artist_file and artist_file.filename:
                try:
                    supa = SupabaseService()
                    contenido = await artist_file.read()
                    artista.foto = supa.subir_imagen(contenido, artist_file.content_type, "artistas")
                except Exception as e:
                    print(f"Error subiendo foto artista: {e}")

            self.session.add(artista)
            self.session.commit()
            self.session.refresh(artista)
            nuevo_artista = artista

            # LIMPIEZA PARCIAL: Borramos SOLO canciones sueltas (top tracks) antiguas para regenerarlas
            # OJO: Mantenemos la lógica de regenerar canciones porque vienen de un Textarea,
            # pero intentaremos no tocar los álbumes si no es necesario.
            canciones_top_viejas = self.session.exec(
                select(Cancion).where(Cancion.artista_id == id_artista, Cancion.album_id == None)
            ).all()
            for c in canciones_top_viejas:
                self.session.delete(c)

        else:
            # MODO CREACIÓN
            url_foto = None
            if artist_file and artist_file.filename:
                try:
                    supa = SupabaseService()
                    contenido = await artist_file.read()
                    url_foto = supa.subir_imagen(contenido, artist_file.content_type, "artistas")
                except:
                    pass

            nuevo_artista = self.repo_artista.crear_artista(
                nombre=nombre,
                nacionalidad=nacionalidad,
                foto=url_foto,
                biografia=biografia,
                genero_principal_id=genero_principal_id
            )

        # ---------------------------------------------------------
        # 2. PROCESAR CANCIONES POPULARES (Sin Álbum)
        # ---------------------------------------------------------
        if top_canciones_texto:
            self._procesar_canciones_texto(nuevo_artista.id_artista, None, top_canciones_texto, genero_principal_id)

        # ---------------------------------------------------------
        # 3. PROCESAR ÁLBUMES (SINCRONIZACIÓN INTELIGENTE)
        # ---------------------------------------------------------

        ids_albumes_procesados = []

        for i, (meta, file_obj) in enumerate(zip(albums_metadata, albums_files)):
            titulo = meta.get('titulo')
            if not titulo: continue

            anio = int(meta.get('anio')) if meta.get('anio') else 2024
            id_existente = meta.get('id_album')  # El ID que enviamos desde el JS

            # Determinar URL de la portada
            cover_url = meta.get('foto_existente')
            if file_obj and file_obj.filename:
                try:
                    supa_alb = SupabaseService()
                    cont_alb = await file_obj.read()
                    cover_url = supa_alb.subir_imagen(cont_alb, file_obj.content_type, "albumes")
                except:
                    pass

            album_obj = None

            if id_existente:
                # --- ACTUALIZAR ÁLBUM EXISTENTE ---
                album_obj = self.session.get(Album, id_existente)
                if album_obj:
                    album_obj.nombre = titulo
                    album_obj.anio_lanzamiento = anio
                    if cover_url:  # Solo cambiamos si hay url válida (nueva o existente)
                        album_obj.foto_portada = cover_url

                    self.session.add(album_obj)
                    print(f"✅ Álbum actualizado: {titulo} (ID: {id_existente})")

            if not album_obj:
                # --- CREAR NUEVO ÁLBUM ---
                # (Si no venía ID o no se encontró en BD)
                print(f"✨ Creando nuevo álbum: {titulo}")
                album_obj = self.repo_album.crear_album(
                    titulo=titulo,
                    artista_id=nuevo_artista.id_artista,
                    anio=anio,
                    cover=cover_url,
                    genero_id=genero_principal_id
                )

            # Guardamos el ID en la lista de "procesados" para no borrarlo después
            self.session.commit()
            self.session.refresh(album_obj)
            ids_albumes_procesados.append(album_obj.id_album)

            # --- GESTIÓN DE CANCIONES DEL ÁLBUM ---
            # Como las canciones vienen en texto plano, es muy difícil hacer "update".
            # Aquí sí aplicamos borrado y recreación, pero SOLO DE LAS CANCIONES DE ESTE ÁLBUM.
            if meta.get('canciones_texto'):
                # 1. Borrar canciones viejas de ESTE álbum específico
                self.session.exec(delete(Cancion).where(Cancion.album_id == album_obj.id_album))
                # 2. Crear las nuevas
                self._procesar_canciones_texto(nuevo_artista.id_artista, album_obj.id_album,
                                               meta.get('canciones_texto'), genero_principal_id)

        # ---------------------------------------------------------
        # 4. LIMPIEZA DE ÁLBUMES HUÉRFANOS
        # ---------------------------------------------------------
        # Si editamos y quitamos un álbum de la lista visual, aquí lo borramos de la BD.
        if id_artista and ids_albumes_procesados:
            albumes_en_bd = self.session.exec(
                select(Album).where(Album.artista_principal_id == id_artista)
            ).all()

            for alb in albumes_en_bd:
                if alb.id_album not in ids_albumes_procesados:
                    print(f"🗑️ Eliminando álbum removido: {alb.nombre}")
                    # Primero borrar sus canciones para evitar FK errors
                    self.session.exec(delete(Cancion).where(Cancion.album_id == alb.id_album))
                    self.session.delete(alb)

            self.session.commit()

        return nuevo_artista.id_artista