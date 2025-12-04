from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import json


# TABLA 1: TELEMETRÍA INTERNA (Lo que hace tu usuario)
class UserEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # ID del usuario (o IP/Session si es anónimo)
    event_type: str  # Ej: "search", "play", "click_artist", "view_genre"

    # Datos específicos del evento en JSON para flexibilidad
    # Ej: {"term": "Rock", "artist_id": "123", "track_features": {"energy": 0.8}}
    payload: str = Field(default="{}")

    timestamp: datetime = Field(default_factory=datetime.utcnow)


# TABLA 2: INTELIGENCIA EXTERNA (Datos procesados de Kaggle)
# Aquí no guardamos las 160k canciones, guardamos los PROMEDIOS y ESTADÍSTICAS.
class ExternalBaseline(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    category: str  # Ej: "genre_stats", "global_averages", "country_popularity"
    key: str  # Ej: "rock", "global", "colombia"

    # Aquí guardamos la "Verdad de Kaggle" pre-calculada
    # Ej: {"avg_energy": 0.6, "avg_valence": 0.4, "top_artists": ["Queen", ...]}
    stats_json: str