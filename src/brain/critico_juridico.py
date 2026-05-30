import ollama
import json

# Coincidencia exacta (normalizada) en estado_del_procedimiento / estado_resumen
ESTADOS_PROCEDIMIENTO_CERRADOS = frozenset({
    "proceso adjudicado y celebrado",
    "adjudicado",
    "adjudicado y celebrado",
    "celebrado",
    "contrato celebrado",
    "desierto",
    "cancelado",
    "terminado",
    "anulado",
    "archivado",
})

# Si el estado contiene alguno de estos fragmentos → proceso sin ventana de participación
FRAGMENTOS_ESTADO_CERRADO = (
    "adjudicado y celebrado",
    "adjudicado y firmado",
    "contrato celebrado",
    "proceso cancelado",
    "declarado desierto",
)

VALORES_ADJUDICACION_VACIOS = frozenset({
    "",
    "no adjudicado",
    "no definido",
    "no informado",
})

PROMPT_V1 = """Eres el Auditor Jurídico Experto en Contratación Pública en Colombia de la Universidad Icesi. Tu misión es auditar el dictamen de un primer agente (El Explorador Semántico) y calibrar su puntaje aplicando una matriz de riesgo basada en la modalidad, el objeto y el estado del contrato.

REGLA PRIORITARIA (APLICA ANTES QUE CUALQUIER OTRA):
0. CASTIGO ABSOLUTO POR PROCESO CERRADO (0% OBLIGATORIO): Si el proceso ya fue adjudicado, celebrado, cancelado, desierto o terminado — o si adjudicado='Si', o estado_resumen='Adjudicado', o id_adjudicacion distinto de 'No Adjudicado' — NO EXISTE ventana de participación. Debes devolver puntaje_ajustado = 0. La modalidad, el objeto o la ventana de tiempo NO pueden elevar el puntaje.

MATRIZ DE RIESGO (SOLO SI EL PROCESO SIGUE ABIERTO A POSTULACIÓN):
1. PENALIZACIÓN LEVE (Reducir 15 a 30 puntos del puntaje original): Si la modalidad es 'Contratación régimen especial', PERO el objeto está claramente relacionado con educación, tecnología, consultoría o investigación.
2. CASTIGO DRÁSTICO (Reducir a 0% - 10% máximo): 
   - Si la modalidad es 'Solicitud de información a los Proveedores'.
   - Si la modalidad es 'Contratación régimen especial' u otra cerrada Y ADEMÁS el objeto es de bienes genéricos o fuera de misionalidad.
3. VÍA LIBRE (Mantener el puntaje original intacto): Si la modalidad es abierta y competitiva y el objeto es pertinente.

FORMATO DE SALIDA ESTRICTAMENTE JSON:
{
  "puntaje_ajustado": <int entre 0 y 100>,
  "justificacion_juridica": "<string>"
}"""

PROMPT_V2 = """Eres el Auditor Jurídico Experto en Contratación Pública en Colombia de la Universidad Icesi. Tu misión es auditar el dictamen de un primer agente (El Explorador Semántico) y calibrar su puntaje aplicando una matriz de riesgo basada en la modalidad, el objeto y el estado del contrato.

REGLA PRIORITARIA (APLICA ANTES QUE CUALQUIER OTRA):
0. CASTIGO ABSOLUTO POR PROCESO CERRADO (0% OBLIGATORIO): Si el proceso ya fue adjudicado, celebrado, cancelado, desierto o terminado — o si adjudicado='Si', o estado_resumen='Adjudicado', o id_adjudicacion distinto de 'No Adjudicado' — NO EXISTE ventana de participación. Debes devolver puntaje_ajustado = 0.

MATRIZ DE RIESGO (SOLO SI EL PROCESO SIGUE ABIERTO A POSTULACIÓN):
1. PENALIZACIÓN LEVE (Reducir 15 a 30 puntos): Modalidad 'Contratación régimen especial' con objeto académico pertinente.
2. CASTIGO DRÁSTICO (0% - 10%): Solicitud de información a proveedores; o régimen especial con objeto operativo/comercial.
3. VÍA LIBRE: Modalidad abierta y objeto pertinente.

FORMATO DE SALIDA ESTRICTAMENTE JSON:
{
  "puntaje_ajustado": <int entre 0 y 100>,
  "justificacion_juridica": "<string>"
}"""


def _normalizar(texto: str) -> str:
    return (texto or "").strip().lower()


def _texto_indica_cierre(texto: str) -> bool:
    norm = _normalizar(texto)
    if not norm or norm in VALORES_ADJUDICACION_VACIOS:
        return False
    if norm in ESTADOS_PROCEDIMIENTO_CERRADOS:
        return True
    return any(fragmento in norm for fragmento in FRAGMENTOS_ESTADO_CERRADO)


def _adjudicacion_efectiva(id_adjudicacion: str) -> bool:
    norm = _normalizar(id_adjudicacion)
    return bool(norm) and norm not in VALORES_ADJUDICACION_VACIOS


def detectar_proceso_cerrado(secop_record: dict) -> tuple[bool, str]:
    """
    Determina si el proceso SECOP ya no admite participación.
    Retorna (cerrado, motivo legible).
    """
    estado = secop_record.get("estado_del_procedimiento", "")
    estado_resumen = secop_record.get("estado_resumen", "")
    adjudicado = _normalizar(str(secop_record.get("adjudicado", "")))
    id_adjudicacion = secop_record.get("id_adjudicacion", "")

    if adjudicado in ("si", "sí", "yes", "true", "1"):
        return True, f"adjudicado='{secop_record.get('adjudicado')}'"

    if _adjudicacion_efectiva(id_adjudicacion):
        return True, f"id_adjudicacion='{id_adjudicacion}'"

    for campo, valor in (
        ("estado_del_procedimiento", estado),
        ("estado_resumen", estado_resumen),
    ):
        if _texto_indica_cierre(str(valor)):
            return True, f"{campo}='{valor}'"

    return False, ""


def _veredicto_cierre(motivo: str) -> dict:
    return {
        "puntaje_ajustado": 0,
        "justificacion_juridica": (
            f"CASTIGO ABSOLUTO (Regla 0 - Proceso cerrado): {motivo}. "
            "El contrato ya fue adjudicado/celebrado o el proceso terminó; "
            "no existe ventana de participación para la Universidad, "
            "independientemente de la modalidad o del objeto."
        ),
    }


class AuditorJuridico:
    def __init__(self, model_name="llama3", use_v2=False):
        self.model_name = model_name
        self.system_prompt = PROMPT_V2 if use_v2 else PROMPT_V1

    def auditar_evaluacion(
        self,
        evaluacion_previa: dict,
        modalidad: str,
        objeto: str,
        estado: str = "",
        secop_record: dict | None = None,
    ) -> dict:
        registro = secop_record or {}
        if estado and not registro.get("estado_del_procedimiento"):
            registro = {**registro, "estado_del_procedimiento": estado}

        cerrado, motivo = detectar_proceso_cerrado(registro)
        if cerrado:
            print(f"  -> [Auditor] Proceso cerrado ({motivo}). Penalización automática 0%.")
            return _veredicto_cierre(motivo)

        adjudicado = registro.get("adjudicado", "No informado")
        estado_resumen = registro.get("estado_resumen", "No informado")
        id_adjudicacion = registro.get("id_adjudicacion", "No informado")
        apertura = registro.get("estado_de_apertura_del_proceso", "No informado")

        prompt = f"""
DATOS DE LA LICITACIÓN:
- Estado del Procedimiento: {registro.get('estado_del_procedimiento') or estado or 'No informado'}
- Estado Resumen: {estado_resumen}
- Adjudicado: {adjudicado}
- ID Adjudicación: {id_adjudicacion}
- Apertura del Proceso: {apertura}
- Modalidad de Contratación: {modalidad}
- Objeto del Contrato: {objeto}

DICTAMEN DEL EXPLORADOR SEMÁNTICO (Primer Agente):
- Viabilidad Propuesta: {evaluacion_previa.get('porcentaje_viabilidad', 0)}%
- Justificación: {evaluacion_previa.get('justificacion_estrategica', 'N/A')}

Si el proceso ya está adjudicado o cerrado, aplica la Regla 0 y responde 0%.
Analiza los datos y emite tu veredicto de auditoría en JSON:
"""

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
            resultado = json.loads(response['message']['content'])

            # Red de seguridad: el LLM no puede saltarse un cierre detectado en metadatos
            cerrado_post, motivo_post = detectar_proceso_cerrado(registro)
            if cerrado_post:
                return _veredicto_cierre(motivo_post)

            return resultado
        except Exception as e:
            print(f"[Auditor] Error en la generación cognitiva: {e}")
            return {
                "puntaje_ajustado": evaluacion_previa.get('porcentaje_viabilidad', 0),
                "justificacion_juridica": "Error en el agente auditor. Se mantiene puntaje original."
            }
