import time
import subprocess
import os
import sys
from datetime import datetime

# Configuración
# Por defecto se ejecutará una vez cada 24 horas (86400 segundos)
# Se puede ajustar mediante la variable de entorno WORKER_INTERVAL_SECONDS
INTERVAL_SECONDS = int(os.getenv("WORKER_INTERVAL_SECONDS", 86400))

def run_pipeline():
    print(f"\n[{datetime.now().isoformat()}] 🚀 [Worker] Iniciando ejecución del pipeline de SARA...")
    
    # Determinamos la ruta del script para compatibilidad tanto local como en Docker
    pipeline_script = os.path.join(os.getcwd(), "run_pipeline.py")
    
    if not os.path.exists(pipeline_script):
        print(f"[{datetime.now().isoformat()}] ❌ [Worker Error] No se encontró el script {pipeline_script}.")
        return False
        
    try:
        # Ejecutamos como subproceso. La salida estándar se pasará directamente al sistema.
        result = subprocess.run(
            [sys.executable, pipeline_script], 
            check=True,
            text=True
        )
        print(f"[{datetime.now().isoformat()}] ✅ [Worker] Pipeline completado con éxito. (Exit code: {result.returncode})")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[{datetime.now().isoformat()}] ⚠️ [Worker Warning] El pipeline falló o retornó código de error: {e.returncode}")
        return False
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] ❌ [Worker Error Crítico] Excepción inmanejable al ejecutar pipeline: {e}")
        return False

def main():
    print("="*60)
    print("🤖 SARA WORKER ORCHESTRATOR INICIADO")
    print(f"⏳ Intervalo de ejecución: {INTERVAL_SECONDS} segundos ({INTERVAL_SECONDS/3600:.1f} horas)")
    print("="*60)
    
    while True:
        # 1. Ejecutar la tarea pesada
        run_pipeline()
        
        # 2. Dormir de forma segura hasta el próximo ciclo
        print(f"[{datetime.now().isoformat()}] 💤 [Worker] Ciclo terminado. Durmiendo por {INTERVAL_SECONDS} segundos...")
        try:
            time.sleep(INTERVAL_SECONDS)
        except KeyboardInterrupt:
            print("\n[Worker] 🛑 Señal de interrupción recibida. Apagando worker de forma segura.")
            break

if __name__ == "__main__":
    main()
