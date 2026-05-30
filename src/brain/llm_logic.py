import ollama
import json

class LlamaEvaluator:
    def __init__(self, model_name="llama3"):
        self.model_name = model_name
        self.system_prompt = """Eres SARA (Sistema Analítico de Recomendación de Adjudicaciones), una Inteligencia Artificial experta en Contratación Pública. Trabajas para la Universidad Icesi evaluando oportunidades de licitación.

REGLAS CRÍTICAS DE EVALUACIÓN:
1. Diccionario Oficial: Usa el 'DICCIONARIO DE CAMPOS' proporcionado por el usuario para entender el significado estratégico de cada variable del JSON.
2. Ventajas Universitarias (Fast-Track): Valora positivamente modalidades como "Ciencia y Tecnología" o "Convenios Interadministrativos", ya que son ventajas legales de la Universidad.
3. Análisis de Tiempo (Neutral): Calcula la ventana exacta entre la fecha de publicación y recepción. No emitas juicios de valor, solo informa los días/horas disponibles.
4. Innovación (Cold Start): Si el contexto RAG indica experiencia previa, aumenta la viabilidad. SI EL RAG ESTÁ VACÍO, NO CASTIGUES LA VIABILIDAD si las condiciones financieras y de tiempo son excelentes. Márcalo como un "Nuevo Nicho" que requiere validación humana.

FORMATO DE SALIDA (ESTRICTAMENTE JSON):
{
  "porcentaje_viabilidad": <int entre 0 y 100>,
  "ventana_de_tiempo": "<string descriptivo del cálculo de tiempo>",
  "justificacion_estrategica": "<string de máximo 3 párrafos justificando la decisión basándote en el diccionario y el RAG>",
  "alertas_criticas": ["<alerta 1>", "<alerta 2>"]
}"""

    def evaluate_process(self, secop_json: dict, rag_context: str, esquema_dict: dict) -> dict:
        prompt = f"DICCIONARIO DE CAMPOS (Reglas Icesi):\n{json.dumps(esquema_dict, indent=2, ensure_ascii=False)}\n\nCONTEXTO HISTÓRICO RAG:\n{rag_context}\n\nPROCESO SECOP A EVALUAR:\n{json.dumps(secop_json, indent=2, ensure_ascii=False)}\n\nGenera la evaluación estructurada en JSON:"
        
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {'role': 'system', 'content': self.system_prompt},
                    {'role': 'user', 'content': prompt}
                ],
                format='json',
                options={'temperature': 0.0}
            )
            return json.loads(response['message']['content'])
        except Exception as e:
            print(f"[LLM] Error en la generación cognitiva: {e}")
            return {"error": str(e)}
