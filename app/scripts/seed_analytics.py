import sys
import os
import json
import random
import pandas as pd
from sqlmodel import Session, select, create_engine

# Añadimos el directorio raíz al path para poder importar 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.analytics import ExternalBaseline
from app.db import engine  # Asumiendo que tienes un engine global, si no, lo creamos abajo

# CONFIGURACIÓN
# Si pones esto en False, buscará los archivos CSV en /data
USE_MOCK_DATA = True


def get_session():
    return Session(engine)


def seed_global_stats(session: Session):
    print("🌍 Generando Línea Base Global (Global Averages)...")

    if USE_MOCK_DATA:
        # Simulamos lo que obtendríamos de df['energy'].mean() del dataset de Tracks
        stats = {
            "avg_energy": 0.65,
            "avg_danceability": 0.58,
            "avg_valence": 0.49,
            "avg_acousticness": 0.30,
            "total_tracks_analyzed": 160000
        }
    else:
        # Lógica real si tuvieras el CSV
        try:
            df = pd.read_csv('data/spotify_tracks.csv')
            stats = {
                "avg_energy": float(df['energy'].mean()),
                "avg_danceability": float(df['danceability'].mean()),
                "avg_valence": float(df['valence'].mean()),
                "total_tracks_analyzed": int(len(df))
            }
        except Exception as e:
            print(f"❌ Error leyendo CSV: {e}")
            return

    # Guardar en DB (Upsert)
    existing = session.exec(select(ExternalBaseline).where(ExternalBaseline.key == "global")).first()
    if not existing:
        existing = ExternalBaseline(category="global_stats", key="global", stats_json="")

    existing.stats_json = json.dumps(stats)
    session.add(existing)
    print("✅ Stats Globales guardadas.")


def seed_genre_stats(session: Session):
    print("🎸 Generando Línea Base por Género...")

    generos_interes = ["rock", "pop", "hip-hop", "jazz", "classical", "reggaeton", "electronic"]

    for genero in generos_interes:
        if USE_MOCK_DATA:
            # Simulamos perfiles de género
            # El Rock es enérgico, el Jazz es tranquilo
            base_energy = 0.8 if genero in ["rock", "reggaeton", "electronic"] else 0.4

            stats = {
                "avg_energy": round(random.uniform(base_energy - 0.1, base_energy + 0.1), 2),
                "avg_valence": round(random.uniform(0.4, 0.8), 2),
                "top_artists": [f"{genero.title()} Artist 1", f"{genero.title()} Artist 2"]
            }
        else:
            # Aquí harías df[df['genre'] == genero]['energy'].mean()
            pass

        # Guardar en DB
        key_name = f"genre_{genero}"
        existing = session.exec(select(ExternalBaseline).where(ExternalBaseline.key == key_name)).first()
        if not existing:
            existing = ExternalBaseline(category="genre_stats", key=key_name, stats_json="")

        existing.stats_json = json.dumps(stats)
        session.add(existing)

    print(f"✅ Stats de {len(generos_interes)} géneros guardadas.")


def run():
    with get_session() as session:
        seed_global_stats(session)
        seed_genre_stats(session)
        session.commit()
        print("\n✨ Sembrado de Analytics completado con éxito.")


if __name__ == "__main__":
    run()