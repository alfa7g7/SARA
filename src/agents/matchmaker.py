import json
import ollama

class MatchmakerAgent:
    def __init__(self, model_name="llama3"):
        self.model_name = model_name
        self.system_prompt = """Eres un Evaluador Experto de Licitaciones Públicas.
Tu objetivo es comparar semánticamente el 'Perfil Institucional' (nuestras capacidades y experiencia) contra la 'Licitación' (requisitos del proceso en SECOP II) para determinar si debemos presentarnos.

REGLAS ESTRICTAS DE SALIDA:
Debes responder ÚNICAMENTE con un JSON válido con esta estructura exacta:
{
  "puntaje_afinidad": 0, // Número entero del 0 al 100
  "puntos_fuertes": [ "Lista de strings. SOLO atributos donde hay coincidencia real. Si no hay coincidencias, devuelve un arreglo vacío []" ],
  "brechas_y_justificacion": [ "Lista de strings. Explica detalladamente por qué no cumplimos, contrastando lo que pide el contrato vs lo que ofrece nuestro perfil" ],
  "recomendacion_final": "Un solo string que sea EXACTAMENTE: 'APLICAR', 'DESCARTAR', o 'BUSCAR CONSORCIO'"
}
No agregues explicaciones fuera del JSON, y asegúrate de que el documento retornado sea un JSON válido.
"""

    def evaluate_match(self, perfil_institucional: dict, licitacion_secop: dict) -> dict:
        """
        Evalúa la compatibilidad entre el perfil y la licitación usando Llama 3.
        """
        prompt = f"--- PERFIL INSTITUCIONAL (Nuestras capacidades) ---\n"
        prompt += json.dumps(perfil_institucional, ensure_ascii=False, indent=2)
        prompt += f"\n\n--- LICITACIÓN (Proceso en SECOP II) ---\n"
        prompt += json.dumps(licitacion_secop, ensure_ascii=False, indent=2)
        prompt += "\n\nAnaliza la información y devuelve la evaluación estructurada en JSON:"
        
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
            
            content = response['message']['content']
            return json.loads(content)
            
        except Exception as e:
            print(f"[Matchmaker Agent] Error durante la evaluación: {e}")
            return {"error": str(e)}
