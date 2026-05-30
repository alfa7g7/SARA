import os
import sqlite3
import argparse
import concurrent.futures
from datetime import datetime, timedelta
from src.ingestion.soda_client import SecopClient
from src.brain.opportunity_evaluator import OpportunityEvaluator
from src.agents.proposal_writer import ProposalWriterAgent
from src.utils.email_notifier import run_notifications

from src.utils.db_manager import get_db_connection

PERFIL_ICESI = {
    "nombre": "Universidad Icesi",
    "enfoque_misional": "Educación superior de excelencia, investigación científica de impacto, proyección social y consultoría integral especializada.",
    "capacidades_tecnicas": "Equipos multidisciplinarios de alto nivel en áreas de Ingeniería, Ciencias de los Datos, Ciencias Administrativas y Económicas, Derecho, Políticas Públicas, Ciencias de la Salud y Ciencias Sociales.",
    "experiencia_ofrecida": "Interventorías técnicas, administrativas y financieras; consultoría en gestión pública y desarrollo empresarial; investigación académica; programas de formación continua; y desarrollo de soluciones tecnológicas e innovación para el Estado."
}

def main():
    parser = argparse.ArgumentParser(description="Orquestador SARA para evaluación masiva de SECOP II.")
    parser.add_argument("--date", type=str, help="Fecha estática para modo de prueba o relleno histórico (YYYY-MM-DD).")
    parser.add_argument("--limit", type=int, default=0, help="Límite máximo de contratos a evaluar (0 = sin límite).")
    args = parser.parse_args()
    
    if args.date:
        target_date = args.date
        print(f"=== INICIANDO SARA MODO HISTÓRICO/PRUEBA ({target_date}) ===")
    else:
        # LÓGICA PRODUCCIÓN: Calcular exactamente el día de ayer (T-1)
        target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        print(f"=== INICIANDO SARA MODO PRODUCCIÓN ({target_date}) ===")
    
    # 1. Ejecutar Ingesta Diaria SODA
    client = SecopClient()
    procesos = client.get_processes_by_date(target_date)
    
    if not procesos:
        print("[Pipeline] No se encontraron nuevos procesos de SECOP II para el dia de hoy.")
        return
        
    if args.limit > 0:
        print(f"[Pipeline] ⚠️ Límite activado: Procesando solo los primeros {args.limit} contratos de {len(procesos)}.")
        procesos = procesos[:args.limit]
        
    # 2. Configurar SQLite para Persistencia y Carpetas
    db_path = os.path.join("data", "historial_sara.sqlite3")
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    propuestas_dir = os.path.join(os.getcwd(), "data", "05_propuestas")
    os.makedirs(propuestas_dir, exist_ok=True)
    
    # 3. Instanciar Motor de Evaluación
    chroma_path = os.path.join(os.getcwd(), "data", "04_vector_db")
    evaluator = OpportunityEvaluator(vector_db_dir=chroma_path)
    
    print(f"\n[Pipeline] Evaluando {len(procesos)} contratos inyectados en el motor LLM...")
    
    # 4. El Bucle Cognitivo
    for proceso in procesos:
        from src.utils.db_manager import get_config
        config = get_config()
        blacklist = config.get("blacklist_palabras", [])
        
        # Sanitización Robusta de variables
        def sanitize_string(val, default):
            if not val:
                return default
            if isinstance(val, dict):
                return str(val.get("url", val.get("url_name", str(val))))
            return str(val)
            
        id_proceso = sanitize_string(proceso.get('id_del_proceso'), 'DESCONOCIDO')
        entidad = sanitize_string(proceso.get('nombre_de_la_entidad', proceso.get('entidad')), 'SIN ENTIDAD')
        objeto = sanitize_string(proceso.get('descripci_n_del_procedimiento', proceso.get('nombre_del_procedimiento')), 'Sin objeto definido')
        
        # Filtro Blacklist
        if any(palabra.lower() in objeto.lower() for palabra in blacklist if palabra.strip()):
            print(f"Skipping {id_proceso} due to blacklist: {objeto[:50]}...")
            continue
        
        referencia = sanitize_string(proceso.get('referencia_del_proceso'), 'No provista')
        url = sanitize_string(proceso.get('urlproceso'), 'No provista')
        
        # Actualizar diccionario para el ProposalWriterAgent
        proceso['urlproceso'] = url
        
        try:
            # ESCUDO DE RESILIENCIA: Envolvemos a Llama 3 en un Hilo con Timeout estricto de 900s (15 min)
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(evaluator.evaluate_secop_opportunity, proceso)
                evaluacion = future.result(timeout=900)
            
            viabilidad = evaluacion.get('porcentaje_viabilidad', 0)
            justificacion = evaluacion.get('justificacion_estrategica', 'La IA no devolvió justificación.')
            
            # Guardar el resultado en la base de datos (INSERT OR REPLACE evita duplicados)
            cursor.execute("""
                INSERT OR REPLACE INTO evaluaciones 
                (id_proceso, entidad, objeto, viabilidad, justificacion, referencia, url) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (id_proceso, entidad, objeto, viabilidad, justificacion, referencia, url))
            conn.commit()
            
            print(f"[SUCCESS] {id_proceso} -> Viabilidad: {viabilidad}% | Guardado en DB.")
            
            from src.utils.db_manager import get_config
            config = get_config()
            umbral_correo = int(config.get("umbral_correo", 70))
            
            # NUEVA COMPUERTA DE NEGOCIO: Redacción de Propuestas
            if viabilidad >= umbral_correo:
                print(f"   🏆 ¡Oportunidad viable detectada! Generando borrador de propuesta...")
                redactor = ProposalWriterAgent()
                propuesta_md = redactor.draft_proposal(perfil_institucional=PERFIL_ICESI, licitacion_secop=proceso)
                
                ruta_propuesta = os.path.join(propuestas_dir, f"{id_proceso}.md")
                with open(ruta_propuesta, 'w', encoding='utf-8') as f:
                    f.write(propuesta_md)
                print(f"   📄 Borrador guardado exitosamente en: {ruta_propuesta}")
            
        except concurrent.futures.TimeoutError:
            print(f"[WARNING] ⏱️ Timeout de 900s superado para el proceso {id_proceso}. Posible falla en Llama 3. Saltando al siguiente.")
            continue
        except Exception as e:
            # Manejo de fallos cognitivos / errores de red
            print(f"[ERROR] Falló la evaluación cognitiva para el proceso {id_proceso}: {e}")
            continue
            
    conn.close()
    
    # Notificación final del Pipeline
    run_notifications()
    
    print("\n=== PIPELINE COMPLETADO EXITOSAMENTE ===")

if __name__ == "__main__":
    main()
