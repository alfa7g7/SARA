import json

# Definición de los dominios de extracción para estructurar la info de los PDFs
# Actualizado con el Diccionario de Datos oficial de SECOP II (SODA API)

DOMINIOS_EXTRACCION = {
    "Dominio_Contexto_Institucional": {
        "descripcion": "Identificación del cliente, su nivel de riesgo y ubicación geográfica.",
        "campos": {
            "entidad": "Nombre de la institución pública que contrata.",
            "ordenentidad": "Orden de la entidad (Nacional o Territorial). Mide el riesgo de pago y origen de recursos.",
            "departamento_entidad": "Departamento de ejecución/ubicación.",
            "ciudad_entidad": "Ciudad exacta de ejecución/ubicación."
        }
    },
    "Dominio_Objeto_y_Especialidad": {
        "descripcion": "Análisis del núcleo técnico del servicio y su forma de adjudicación.",
        "campos": {
            "nombre_del_procedimiento": "Título corto y objeto principal del proceso.",
            "descripci_n_del_procedimiento": "Descripción detallada del alcance técnico requerido.",
            "codigo_principal_de_categoria": "Código UNSPSC primario. Define objetivamente el núcleo del servicio.",
            "categorias_adicionales": "Códigos UNSPSC secundarios para evitar sesgos.",
            "numero_de_lotes": "Indica si el proceso permite participación parcial (Lotes) o requiere ejecución integral."
        }
    },
    "Dominio_Contractual_y_Legal": {
        "descripcion": "Reglas jurídicas, tipo de vínculo y atajos legales aplicables.",
        "campos": {
            "tipo_de_contrato": "Marco jurídico general (ej. Prestación de servicios).",
            "subtipo_de_contrato": "Clasificación específica (ej. Consultoría, Ciencia y Tecnología).",
            "modalidad_de_contratacion": "Mecanismo de selección (ej. Licitación, Mínima cuantía).",
            "justificaci_n_modalidad_de": "Argumento legal de selección. Vital para detectar convenios interadministrativos o ciencia/tecnología (Fast-Tracks para universidades).",
            "estado_del_procedimiento": "Estado general actual (Filtro para evitar procesos ya cerrados o cancelados).",
            "fase": "Fase legal exacta en el SECOP (ej. Borrador, Observaciones). Define el margen de acción de la Universidad."
        }
    },
    "Dominio_Financiero_y_Tiempos": {
        "descripcion": "Viabilidad presupuestal y plazos críticos de reloj. SARA debe extraer las fechas y calcular matemáticamente la ventana de tiempo exacta (días/horas) que queda disponible, para que el equipo humano determine si es operativamente viable participar.",
        "campos": {
            "fecha_de_publicacion_del": "Fecha de la publicación inicial del proceso. Vital para cruzar con la fecha de recepción y calcular el tiempo exacto en días/horas que tiene la Universidad para preparar y enviar la propuesta (ventana de postulación).",
            "precio_base": "Presupuesto oficial proyectado ($ COP).",
            "duracion": "Valor numérico del tiempo estimado de ejecución.",
            "unidad_de_duracion": "Unidad de medida (Meses, Días).",
            "fecha_de_recepcion_de": "Fecha límite para presentar la propuesta (El 'Deadline' absoluto)."
        }
    }
}

def get_schema_prompt(dominio: str) -> str:
    """Genera un string con las instrucciones del esquema para el prompt del LLM."""
    if dominio not in DOMINIOS_EXTRACCION:
        return ""
        
    info = DOMINIOS_EXTRACCION[dominio]
    prompt = f"Dominio a extraer: {dominio}\n"
    prompt += f"Descripción: {info['descripcion']}\n\n"
    prompt += "Los campos exactos que debes extraer y sus descripciones son:\n"
    
    for campo, desc in info['campos'].items():
        prompt += f"- \"{campo}\": (string) {desc}\n"
        
    prompt += "\nSi la información de un campo no se menciona explícitamente en el texto, el valor debe ser null. NO inventes ni deduzcas datos."
    return prompt