import ollama
import json

class ProposalWriterAgent:
    def __init__(self, model_name="llama3"):
        self.model_name = model_name
        self.system_prompt = """Eres el Director de Licitaciones de la Universidad Icesi.
Tu objetivo es redactar un borrador de propuesta técnica persuasiva y profesional basada en el 'Perfil Institucional' y los requisitos del 'Contrato SECOP'.

REGLAS ESTRICTAS DE SALIDA:
Debes generar un documento estructurado en formato Markdown con las siguientes secciones obligatorias:
1. Resumen Ejecutivo (Contexto general y propuesta de valor de Icesi).
2. Enfoque Técnico (Cómo la Universidad Icesi resolverá la necesidad específica del estado de forma innovadora y académica).
3. Experiencia Previa (Destacando la experiencia y capacidades del perfil institucional proporcionado).

* No incluyas comentarios, saludos ni despedidas. Solo entrega el documento Markdown.
* El tono debe ser altamente profesional, institucional, académico y persuasivo.
"""

    def draft_proposal(self, perfil_institucional: dict, licitacion_secop: dict) -> str:
        """
        Genera el borrador de la propuesta en Markdown usando Llama 3.
        """
        prompt = f"--- PERFIL INSTITUCIONAL (Nuestras capacidades) ---\n"
        prompt += json.dumps(perfil_institucional, ensure_ascii=False, indent=2)
        prompt += f"\n\n--- CONTRATO SECOP (Lo que el estado necesita) ---\n"
        prompt += json.dumps(licitacion_secop, ensure_ascii=False, indent=2)
        prompt += "\n\nRedacta el borrador de la propuesta en formato Markdown según las reglas establecidas:"
        
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {'role': 'system', 'content': self.system_prompt},
                    {'role': 'user', 'content': prompt}
                ],
                options={'temperature': 0.7} # Mayor temperatura para creatividad en la redacción
            )
            
            contenido = response['message']['content']
            
            # Inyección de Trazabilidad SECOP
            variable_id = licitacion_secop.get('id_del_proceso', 'No disponible')
            variable_referencia = licitacion_secop.get('referencia_del_proceso', 'No disponible')
            variable_url = licitacion_secop.get('urlproceso', '#')
            
            trazabilidad = f"""

### 🔗 Referencias Oficiales
- **ID del Proceso:** {variable_id}
- **Referencia:** {variable_referencia}
- **Enlace SECOP II:** {variable_url}
"""
            return contenido + trazabilidad
            
        except Exception as e:
            print(f"[Proposal Writer Agent] Error durante la redacción: {e}")
            return f"Error generando la propuesta: {e}"
