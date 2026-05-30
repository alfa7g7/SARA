import os
import json
from sodapy import Socrata
from dotenv import load_dotenv

# Cargar variables de entorno (App Token y tokens de usuario)
load_dotenv()

class SecopClient:
    def __init__(self):
        """
        Inicializa el cliente de SODA 3 para www.datos.gov.co
        Usando exclusivamente App Token y Secret Token/Contraseña según directrices.
        Ignorando API Keys tradicionales.
        """
        self.domain = "www.datos.gov.co"
        self.dataset_id = "p6dx-8zbt" # SECOP II - Procesos de Contratación
        
        self.app_token = os.getenv("SODA_APP_TOKEN")
        
        # En sodapy, si se provee password, es obligatorio proveer username.
        # Si el usuario no lo define en el .env, Socrata funcionará solo con el App Token
        # para datos públicos como SECOP II, garantizando la extracción sin fallos 403.
        self.username = os.getenv("SODA_USER_EMAIL")
        self.password = os.getenv("SODA_USER_PASSWORD")
        
        if self.app_token and self.username and self.password:
            self.client = Socrata(
                self.domain, 
                self.app_token, 
                username=self.username, 
                password=self.password, 
                timeout=120
            )
        else:
            self.client = Socrata(
                self.domain, 
                self.app_token,
                timeout=120
            )

    def get_processes_by_date(self, target_date: str) -> list[dict]:
        """
        Consulta el dataset de SECOP II extrayendo todos los procesos de una fecha.
        Guarda los resultados físicamente en disco garantizando la persistencia.
        """
        print(f"[SODA Client] Consultando contratos nacionales del día {target_date}...")
        try:
            results = self.client.get(
                self.dataset_id, 
                limit=50000,
                where=f"fecha_de_publicacion_del >= '{target_date}T00:00:00' AND fecha_de_publicacion_del <= '{target_date}T23:59:59'", 
                #where=f"starts_with(fecha_de_publicacion_del, '{target_date}')",
                order="fecha_de_publicacion_del DESC"
            )
            
            # Guardado Físico (Persistencia)
            output_dir = os.path.join(os.getcwd(), "data", "02_raw_secop")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"procesos_{target_date}.json")
            
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=4, ensure_ascii=False)
                
            print(f"[SODA Client] Operación exitosa. {len(results)} registros almacenados en: {output_path}")
            return results
            
        except Exception as e:
            print(f"[!] Error consultando la API de SODA: {e}")
            return []

    def get_process_by_id(self, id_proceso: str) -> dict:
        """
        Consulta la API de SODA para traer la metadata completa de un ID de proceso específico.
        Útil para procesos de enriquecimiento de datos (Hydration).
        """
        try:
            results = self.client.get(
                self.dataset_id, 
                where=f"id_del_proceso = '{id_proceso}'"
            )
            return results[0] if results else {}
        except Exception as e:
            print(f"[!] Error extrayendo ID {id_proceso}: {e}")
            return {}
