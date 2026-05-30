import json
from src.brain.vector_db import VectorDBContext
from src.brain.llm_logic import LlamaEvaluator
from src.brain.schemas import DOMINIOS_EXTRACCION
from src.brain.critico_juridico import AuditorJuridico

from src.utils.db_manager import get_config

class OpportunityEvaluator:
    def __init__(self, vector_db_dir: str):
        self.vector_db = VectorDBContext(persist_directory=vector_db_dir)
        self.llm = LlamaEvaluator()
        
        config = get_config()
        estricto = config.get("auditor_estricto", True)
        self.auditor = AuditorJuridico(use_v2=not estricto)
        
    def evaluate_secop_opportunity(self, secop_record: dict) -> dict:
        print(f"\n[SARA Brain] Iniciando evaluación para proceso: {secop_record.get('id_del_proceso', 'DESCONOCIDO')}")
        
        # 1. Búsqueda en Memoria (RAG)
        search_query = secop_record.get('descripci_n_del_procedimiento', secop_record.get('nombre_del_procedimiento', 'Proceso de contratación'))
        print(f"  -> Consultando memoria institucional para: {search_query[:60]}...")
        
        results = self.vector_db.search(search_query, top_k=3)
        
        rag_context = ""
        if results and results.get('documents') and len(results['documents'][0]) > 0:
            rag_context = "\n\n".join(results['documents'][0])
            print("  -> [HIT] Contexto histórico recuperado exitosamente.")
        else:
            print("  -> [MISS] Sin historial. Evaluando como oportunidad de innovación (Nuevo Nicho).")
            rag_context = "No hay historial previo en la Universidad. Evaluar como posible nuevo nicho basándose puramente en viabilidad legal, técnica y financiera."
            
        # 2. Evaluación Cognitiva (Explorador Semántico)
        print("  -> Transfiriendo datos al motor Llama 3 (Explorador) para dictamen inicial...")
        evaluacion = self.llm.evaluate_process(secop_json=secop_record, rag_context=rag_context, esquema_dict=DOMINIOS_EXTRACCION)
        
        # 3. Auditoría Jurídica (Segundo Agente)
        print("  -> Activando Agente Crítico Jurídico...")
        modalidad = secop_record.get("modalidad_de_contratacion", "Desconocida")
        objeto = secop_record.get("descripci_n_del_procedimiento", secop_record.get("nombre_del_procedimiento", ""))
        auditoria = self.auditor.auditar_evaluacion(
            evaluacion_previa=evaluacion,
            modalidad=modalidad,
            objeto=objeto,
            secop_record=secop_record,
        )
        
        # 4. Integración y Trazabilidad Multi-Agente
        puntaje_previo = evaluacion.get("porcentaje_viabilidad", 0)
        justificacion_previa = evaluacion.get("justificacion_estrategica", "Sin justificación inicial.")
        
        puntaje_ajustado = auditoria.get("puntaje_ajustado", puntaje_previo)
        justificacion_critico = auditoria.get("justificacion_juridica", "Fallo en el reporte del auditor.")
        
        # Reemplazo Absoluto
        evaluacion["porcentaje_viabilidad"] = puntaje_ajustado
        
        # Concatenación Estricta de la Justificación
        evaluacion["justificacion_estrategica"] = f"[Explorador Semántico - {puntaje_previo}%]: {justificacion_previa}\n\n[🔴 AUDITORÍA JURÍDICA - {puntaje_ajustado}%]: {justificacion_critico}"
        
        print("  -> [ÉXITO] Evaluación Multi-Agente completada.")
        return evaluacion
