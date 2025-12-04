import os
import time
from typing import Optional
from supabase import create_client, Client


class SupabaseService:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        self.bucket = os.getenv("SUPABASE_BUCKET", "sonicore-music")

        if url and key:
            self.client = create_client(url, key)
        else:
            self.client = None
            print("⚠️ Supabase no configurado en .env")

    def subir_imagen(self, archivo_bytes, tipo_contenido, carpeta="artistas"):
        if not self.client: return None
        try:
            # Nombre único para no sobrescribir
            nombre_archivo = f"{carpeta}/{int(time.time())}.{tipo_contenido.split('/')[-1]}"

            # Subir
            self.client.storage.from_(self.bucket).upload(
                path=nombre_archivo,
                file=archivo_bytes,
                file_options={"content-type": tipo_contenido}
            )

            # Obtener URL Pública
            return self.client.storage.from_(self.bucket).get_public_url(nombre_archivo)
        except Exception as e:
            print(f"❌ Error Supabase: {e}")
            return None