from sqlmodel import Session, select
from app.models.analytics import UserEvent, ExternalBaseline
from datetime import datetime, timedelta
import json
from sqlalchemy import func


class AnalyticsService:
    def __init__(self, session: Session):
        self.session = session

    # ... (MANTENER LA PARTE A: RECOLECCIÓN DE DATOS IGUAL) ...
    def registrar_evento(self, user_id: str, tipo: str, datos: dict):
        """Guarda un evento sin bloquear la respuesta principal (Fire & Forget)"""
        nuevo_evento = UserEvent(
            user_id=user_id,
            event_type=tipo,
            payload=json.dumps(datos),
            timestamp=datetime.utcnow()
        )
        self.session.add(nuevo_evento)
        self.session.commit()
        return {"status": "ok"}

    # ... (MANTENER INSIGHT 1 y 2 IGUALES) ...

    # INSIGHT 1: "El Explorador"
    def analizar_explorador(self, user_id: str):
        hace_semana = datetime.utcnow() - timedelta(days=7)
        query = select(UserEvent).where(
            UserEvent.user_id == user_id,
            UserEvent.event_type.in_(["play", "view_genre"]),  # Mejorado para capturar ambos
            UserEvent.timestamp >= hace_semana
        )
        eventos = self.session.exec(query).all()

        generos_vistos = set()
        for ev in eventos:
            data = json.loads(ev.payload)
            if 'genre' in data: generos_vistos.add(data['genre'])
            if 'section' in data: generos_vistos.add(data['section'])  # Para navegación

        count = len(generos_vistos)
        mensaje = ""
        if count > 5:
            mensaje = f"🚀 ¡Eres un explorador! Has visitado {count} géneros distintos."
        elif count > 2:
            mensaje = f"Estás ampliando horizontes: {count} géneros esta semana."
        else:
            mensaje = "Estás en tu zona de confort musical."

        return {"score": count, "mensaje": mensaje, "generos": list(generos_vistos)}

    # INSIGHT 2: "Búho Nocturno"
    def analizar_horarios(self, user_id: str):
        query = select(UserEvent.timestamp).where(
            UserEvent.user_id == user_id,
            UserEvent.event_type == "play"
        )
        timestamps = self.session.exec(query).all()

        if not timestamps: return {"mensaje": "No hay suficientes datos aún."}

        horas_noche = sum(1 for t in timestamps if t.hour >= 22 or t.hour <= 4)
        total = len(timestamps)
        porcentaje_noche = (horas_noche / total) * 100

        # Aquí podrías traer esto de ExternalBaseline también si quisieras
        promedio_mundial_noche = 15

        comparativa = "más" if porcentaje_noche > promedio_mundial_noche else "menos"
        return {
            "porcentaje_noche": round(porcentaje_noche, 1),
            "mensaje": f"Escuchas un {round(porcentaje_noche)}% de tu música en la madrugada.",
            "insight": f"Eres {comparativa} nocturno que el promedio mundial ({promedio_mundial_noche}%)."
        }

    # --- CAMBIO CRÍTICO AQUÍ 👇 ---

    # INSIGHT 3: Comparativa de Energía (Data-Driven Real)
    def comparar_energia(self, user_id: str):
        # 1. Calcular promedio del usuario (Telemetría Interna)
        eventos = self.session.exec(
            select(UserEvent).where(UserEvent.user_id == user_id, UserEvent.event_type == "play")).all()
        energias = []
        for ev in eventos:
            d = json.loads(ev.payload)
            # Buscamos 'energy' en varios lugares por robustez
            energy = d.get('energy') or d.get('audio_features', {}).get('energy')
            if energy:
                energias.append(float(energy))

        if not energias:
            return {"mensaje": "Escucha más música para calibrar tu energía."}

        avg_user = sum(energias) / len(energias)

        # 2. Obtener Baseline Externa (Desde la DB, NO hardcodeado)
        baseline = self.session.exec(select(ExternalBaseline).where(ExternalBaseline.key == "global")).first()

        if baseline:
            stats = json.loads(baseline.stats_json)
            avg_global = stats.get("avg_energy", 0.65)  # Fallback seguro
        else:
            avg_global = 0.65  # Fallback si no se corrió el seeder

        diff = avg_user - avg_global
        estado = "más intenso" if diff > 0 else "más tranquilo"
        porcentaje = abs(round(diff * 100))

        return {
            "tu_energia": round(avg_user, 2),
            "global_energia": avg_global,
            "mensaje": f"Tu gusto musical es un {porcentaje}% {estado} que el promedio global.",
            "detalle": f"Tú: {round(avg_user, 2)} vs Mundo: {avg_global}"
        }