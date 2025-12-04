# 🎵 SONICORE – Plataforma de Gestión Musical Inteligente

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)  
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688)  
![SQLModel](https://img.shields.io/badge/ORM-SQLModel-green)  
![Spotify API](https://img.shields.io/badge/Spotify-Integration-1DB954)  
![Supabase](https://img.shields.io/badge/Storage-Supabase-3ECF8E)  

**SONICORE** es una plataforma web híbrida que combina la gestión de una biblioteca musical local con la potencia de la nube.  
Permite administrar tu música con CRUD completo, importar metadatos enriquecidos desde Spotify, visualizar estadísticas avanzadas de tus hábitos de escucha y disfrutar de una interfaz inmersiva con diseño *Glassmorphism*.  

---

## ✨ Características

### 🎧 Gestión Híbrida de Música
- **Biblioteca Local:** CRUD completo sobre Artistas, Álbumes, Canciones y Géneros.  
- **Importación Inteligente:** Conexión directa con la API de Spotify para importar artistas/álbumes con metadatos completos (portadas, fechas, duración).  
- **Favoritos Persistentes:** Sistema de "Me gusta/No me gusta" almacenado en la base de datos.  

### 📊 Analytics & Insights
- **ADN Musical:** Algoritmo que compara la energía promedio de tu biblioteca con estadísticas globales.  
- **Patrones de Escucha:** Detección automática de hábitos (ej. *Búho Nocturno*).  
- **Radar Charts:** Visualización interactiva de características de audio (*Bailabilidad, Energía, Valencia, Acústica, Instrumentalidad*).  

### 🎨 Experiencia de Usuario
- **Glassmorphism UI:** Interfaz moderna con transparencias, desenfoques y gradientes de neón.  
- **Modales Dinámicos:** Edición de artistas y álbumes sin recargar la página.  
- **Reproductor Persistente:** Barra flotante conectada a la sesión de Spotify del usuario.  

---

## 🛠️ Stack Tecnológico

| Capa        | Tecnologías |
|-------------|-------------|
| **Backend** | FastAPI, SQLModel, OAuth 2.0 (Spotify), Spotipy, Supabase |
| **Frontend**| Jinja2, CSS3 (Flexbox, Grid, Variables), JavaScript ES6+, Chart.js |
| **Infraestructura** | PostgreSQL, Supabase Storage (S3 compatible) |

---

## ⚙️ Instalación y Configuración

### 1. Prerrequisitos
- Python 3.10+  
- Cuenta en [Spotify for Developers](https://developer.spotify.com/)  
- Cuenta en [Supabase](https://supabase.com/)  
- PostgreSQL local o remoto  

### 2. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/sonicore.git
cd sonicore
```

### 3. Crear entorno virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 5. Configurar variables de entorno
Crea un archivo `.env` en la raíz del proyecto:

```ini
# Base de Datos
DATABASE_URL="postgresql://postgres:admin@localhost:5432/sonicore_db"

# Spotify API
SPOTIFY_CLIENT_ID="tu_client_id_aqui"
SPOTIFY_CLIENT_SECRET="tu_client_secret_aqui"

# Supabase
SUPABASE_URL="https://tu-proyecto.supabase.co"
SUPABASE_KEY="tu_anon_public_key"
SUPABASE_BUCKET="sonicore-music"
```

⚠️ Importante: Configura la **Redirect URI** en Spotify como:  
`http://127.0.0.1:8000/callback`

---

## 🚀 Inicialización

1. **Preparar la base de datos**
```bash
python reset_db.py
```

2. **Sembrar datos de Analytics**
```bash
python -m app.scripts.seed_analytics
```

3. **Ejecutar servidor**
```bash
uvicorn app.main:app --reload
```

La aplicación estará disponible en:  
👉 `http://127.0.0.1:8000`

---

## 📂 Estructura del Proyecto

```
sonicore/
├── app/
│   ├── models/          # Modelos SQLModel
│   ├── routers/         # Endpoints FastAPI
│   ├── repositories/    # CRUD y acceso a datos
│   ├── services/        # Lógica de negocio (Spotify, Analytics, Supabase)
│   ├── scripts/         # Seeders e inicialización
│   ├── database.py      # Conexión a BD
│   └── main.py          # Punto de entrada FastAPI
├── static/              # CSS, JS, imágenes
├── templates/           # Plantillas Jinja2
├── .env                 # Variables de entorno
├── requirements.txt     # Dependencias
└── reset_db.py          # Script de reseteo BD
```

---

## 📖 Guía de Uso

- **Login con Spotify:** Conéctate para habilitar el reproductor y la importación personalizada.  
- **Dashboard:** Visualiza insights sobre tu gusto musical y navega por artistas, álbumes y canciones locales.  
- **Importar Música:** Usa la barra de búsqueda → "Buscar en Spotify" → "Importar".  
- **Modales de Edición:** Edita artistas/álbumes, sube fotos a Supabase o añade canciones manualmente.  

---

## 🤝 Contribución

1. Haz un **Fork** del proyecto.  
2. Crea una rama:  
   ```bash
   git checkout -b feature/NuevaFuncionalidad
   ```  
3. Commit de tus cambios:  
   ```bash
   git commit -m "Agrega nueva funcionalidad"
   ```  
4. Push a tu rama:  
   ```bash
   git push origin feature/NuevaFuncionalidad
   ```  
5. Abre un **Pull Request**.  

---

## 📄 Licencia

Autora: Karen Zapata - 67001322