import pandas as pd
import random

class DatasetService:
    def __init__(self):
        # Simulamos cargar un CSV de Kaggle con 1000 canciones
        # En un proyecto real: self.df = pd.read_csv("data/spotify_dataset.csv")
        datos = {
            "genero": ["Pop", "Rock", "Reggaeton", "Jazz", "Hip-Hop"] * 200,
            "energia": [random.uniform(0.4, 0.9) for _ in range(1000)],
            "bailabilidad": [random.uniform(0.3, 0.95) for _ in range(1000)],
            "popularidad": [random.randint(10, 100) for _ in range(1000)],
            "titulo": [f"Track {i}" for i in range(1000)]
        }
        self.df = pd.DataFrame(datos)

    def reporte_generos(self):
        """Promedio de energía y bailabilidad por género"""
        return self.df.groupby("genero")[["energia", "bailabilidad"]].mean().reset_index().to_dict(orient="records")

    def top_historico(self):
        """Top 5 canciones históricas del dataset"""
        return self.df.sort_values(by="popularidad", ascending=False).head(5).to_dict(orient="records")