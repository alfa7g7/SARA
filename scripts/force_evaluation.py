import os
import sys
import json
import sqlite3

# Resolver importaciones relativas si se corre desde scripts/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.brain.opportunity_evaluator import OpportunityEvaluator
from src.agents.proposal_writer import ProposalWriterAgent
from src.utils.email_notifier import run_notifications
from src.ingestion.soda_client import SecopClient

PERFIL_ICESI = {
    "nombre": "Universidad Icesi",
    "enfoque_misional": "Educación superior de excelencia, investigación científica de impacto, proyección social y consultoría integral especializada.",
    "capacidades_tecnicas": "Equipos multidisciplinarios de alto nivel en áreas de Ingeniería, Ciencias de los Datos, Ciencias Administrativas y Económicas, Derecho, Políticas Públicas, Ciencias de la Salud y Ciencias Sociales.",
    "experiencia_ofrecida": "Interventorías técnicas, administrativas y financieras; consultoría en gestión pública y desarrollo empresarial; investigación académica; programas de formación continua; y desarrollo de soluciones tecnológicas e innovación para el Estado."
}

def main():
    json_path = os.path.join("data", "04_outputs", "golden_truth.json")
    db_path = os.path.join("data", "historial_sara.sqlite3")
    chroma_path = os.path.join("data", "04_vector_db")
    propuestas_dir = os.path.join("data", "05_propuestas")
    os.makedirs(propuestas_dir, exist_ok=True)
    
    # 1. Validación de Archivos
    if not os.path.exists(json_path):
        print(f"[ERROR] No se encontró el archivo Golden Truth en: {json_path}")
        return

    # 2. Leer Golden Truth
    with open(json_path, 'r', encoding='utf-8') as f:
        golden_data = json.load(f)
        
    # Normalizar formato a lista de diccionarios
    if isinstance(golden_data, dict):
        items = []
        for k, v in golden_data.items():
            if isinstance(v, dict):
                v["id_proceso"] = v.get("id_proceso", k)
                items.append(v)
        golden_data = items

    # 3. Conexión a Base de Datos Centralizada
    from src.utils.db_manager import get_db_connection
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    # Extraer IDs que SARA ya evaluó
    cursor.execute("SELECT id_proceso FROM evaluaciones")
    existentes = {row[0] for row in cursor.fetchall()}
    
    # Cruzar para encontrar los "Pendientes"
    pendientes = [item for item in golden_data if item.get("id_proceso") and item.get("id_proceso") not in existentes]
    
    if not pendientes:
        print("✅ ¡Magnífico! Todos los contratos del Golden Truth ya han sido evaluados por SARA.")
        conn.close()
        return
        
    print("="*60)
    print(f"⚠️  INICIANDO EVALUACIÓN FORZADA ({len(pendientes)} contratos pendientes)")
    print("="*60)
    
    # 4. Inicialización del Motor Cognitivo y SODA
    print("[Sistema] Cargando la memoria institucional (ChromaDB) y encendiendo Llama 3...")
    evaluator = OpportunityEvaluator(vector_db_dir=chroma_path)
    secop_client = SecopClient()
    
    # 5. Bucle de Evaluación e Inyección Forzada
    for i, proceso in enumerate(pendientes, 1):
        id_proceso = proceso.get("id_proceso", "DESCONOCIDO")
        
        # PATRÓN DE DATA HYDRATION: Enriquecimiento del Golden Truth
        # Consultamos SECOP para traer Entidad, URL y demás metadata que fue purgada del JSON
        print(f"\n[{i}/{len(pendientes)}] 🔄 SARA Hidratando contrato {id_proceso} desde SECOP...")
        metadata_oficial = secop_client.get_process_by_id(id_proceso)
        
        # Mezclamos la data oficial con la del Golden Truth para que Llama 3 tenga todo
        proceso.update(metadata_oficial)
        
        # Corrección de "DESCONOCIDO": Asegurar que exista la llave 'id_del_proceso' para el Evaluator
        proceso['id_del_proceso'] = id_proceso
        
        # Sanitización Robusta de variables (evitar SQLite Error type 'dict' is not supported)
        def sanitize_string(val, default):
            if not val:
                return default
            if isinstance(val, dict):
                return str(val.get("url", val.get("url_name", str(val))))
            return str(val)
        
        # Extracción segura de metadata para persistencia
        entidad = sanitize_string(proceso.get("nombre_de_la_entidad", proceso.get("entidad")), "SIN ENTIDAD")
        objeto = sanitize_string(proceso.get("descripci_n_del_procedimiento", proceso.get("objeto_real")), "Sin objeto definido")
        referencia = sanitize_string(proceso.get("referencia_del_proceso"), "No provista")
        url = sanitize_string(proceso.get("urlproceso"), "No provista")
        
        # Limpieza dentro del diccionario en memoria para que no falle el ProposalWriter
        proceso['urlproceso'] = url
        proceso['nombre_de_la_entidad'] = entidad
        proceso['referencia_del_proceso'] = referencia
        
        print(f"[{i}/{len(pendientes)}] 🧠 Analizando viabilidad de la oportunidad...")
        
        try:
            # Invocar RAG + Inferencia
            evaluacion = evaluator.evaluate_secop_opportunity(proceso)
            
            viabilidad = evaluacion.get('porcentaje_viabilidad', 0)
            justificacion = evaluacion.get('justificacion_estrategica', 'La IA no devolvió justificación.')
            
            # Guardado Transaccional (Upsert)
            cursor.execute("""
                INSERT OR REPLACE INTO evaluaciones 
                (id_proceso, entidad, objeto, viabilidad, justificacion, referencia, url) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (id_proceso, entidad, objeto, viabilidad, justificacion, referencia, url))
            conn.commit()
            
            print(f"   ✅ [ÉXITO] Viabilidad dictaminada: {viabilidad}% | Guardado en Historial DB.")
            
            # NUEVA COMPUERTA DE NEGOCIO: Redacción de Propuestas
            if viabilidad >= 70:
                print(f"   🏆 ¡Oportunidad viable detectada! Generando borrador de propuesta...")
                redactor = ProposalWriterAgent()
                propuesta_md = redactor.draft_proposal(perfil_institucional=PERFIL_ICESI, licitacion_secop=proceso)
                
                ruta_propuesta = os.path.join(propuestas_dir, f"{id_proceso}.md")
                with open(ruta_propuesta, 'w', encoding='utf-8') as f:
                    f.write(propuesta_md)
                print(f"   📄 Borrador guardado exitosamente en: {ruta_propuesta}")
            
        except Exception as e:
            print(f"   ❌ [ERROR CRÍTICO] Falló la evaluación cognitiva para {id_proceso}: {e}")
            continue
            
    conn.close()
    
    # Notificación final tras la inyección forzada
    run_notifications()
    
    print("\n" + "="*60)
    print("🏁 OPERACIÓN COMPLETADA. Puedes correr run_evaluation.py nuevamente.")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
