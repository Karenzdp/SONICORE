import sys
import os

# CRÍTICO: Agregar el directorio raíz al path
proyecto_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, proyecto_root)

import json
import random
from sqlmodel import Session, select

# Importar desde dependencies (no db)
from app.dependencies import engine
from app.models.analytics import ExternalBaseline, UserEvent


def get_session():
    return Session(engine)


def crear_tablas_analytics():
    """Crear las tablas de analytics si no existen"""
    print("📊 Verificando tablas de analytics...")
    from sqlmodel import SQLModel

    # Importar modelos para que SQLModel los registre
    from app.models.analytics import ExternalBaseline, UserEvent

    SQLModel.metadata.create_all(engine)
    print("✅ Tablas verificadas/creadas")


def seed_global_stats(session: Session):
    print("🌍 Generando Línea Base Global...")

    stats = {
        "avg_energy": 0.65,
        "avg_danceability": 0.58,
        "avg_valence": 0.49,
        "avg_acousticness": 0.30,
        "total_tracks_analyzed": 160000
    }

    existing = session.exec(select(ExternalBaseline).where(
        ExternalBaseline.key == "global"
    )).first()

    if not existing:
        existing = ExternalBaseline(
            category="global_stats",
            key="global",
            stats_json=""
        )

    existing.stats_json = json.dumps(stats)
    session.add(existing)
    session.flush()
    print("✅ Stats Globales guardadas.")


def seed_genre_stats(session: Session):
    print("🎸 Generando Línea Base por Género...")

    generos_interes = ["rock", "pop", "hip-hop", "jazz", "classical", "reggaeton", "electronic"]

    for genero in generos_interes:
        base_energy = 0.8 if genero in ["rock", "reggaeton", "electronic"] else 0.4

        stats = {
            "avg_energy": round(random.uniform(base_energy - 0.1, base_energy + 0.1), 2),
            "avg_valence": round(random.uniform(0.4, 0.8), 2),
            "top_artists": [f"{genero.title()} Artist 1", f"{genero.title()} Artist 2"]
        }

        key_name = f"genre_{genero}"
        existing = session.exec(select(ExternalBaseline).where(
            ExternalBaseline.key == key_name
        )).first()

        if not existing:
            existing = ExternalBaseline(
                category="genre_stats",
                key=key_name,
                stats_json=""
            )

        existing.stats_json = json.dumps(stats)
        session.add(existing)

    session.flush()
    print(f"✅ Stats de {len(generos_interes)} géneros guardadas.")


def run():
    print("\n" + "=" * 60)
    print("🚀 INICIANDO SEEDER DE ANALYTICS")
    print("=" * 60 + "\n")

    try:
        # Crear tablas primero
        crear_tablas_analytics()

        # Poblar datos
        with get_session() as session:
            seed_global_stats(session)
            seed_genre_stats(session)
            session.commit()
            print("\n✨ Sembrado de Analytics completado con éxito.\n")
            print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    run()