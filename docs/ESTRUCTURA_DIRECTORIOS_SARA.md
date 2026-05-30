# Arquitectura y Estructura de Directorios de SARA (Detallada)

Este documento detalla la estructura lógica del ecosistema SARA con precisión quirúrgica. El proyecto aplica el principio de **Separación de Responsabilidades** (*Separation of Concerns*) y **Arquitectura Limpia** (*Clean Architecture*). La premisa principal es separar los datos físicos (bases y logs), los puntos de ejecución (orquestadores y scripts) y la lógica de negocio subyacente (módulos reutilizables).

---

## 🌳 Directorio Raíz (`/SARA`)

La raíz se mantiene minimalista. Funciona estrictamente como la capa de configuración e instanciación de servicios.

*   `run_pipeline.py`: **Worker Principal.** Es el orquestador maestro (CLI) que se ejecuta en el día a día. Encapsula las llamadas a SODA API, invoca a Llama 3 para la inferencia RAG y activa los envíos por correo.
*   `run_evaluation.py`: **Módulo de Benchmarking.** Orquestador que itera sobre un conjunto de datos controlado (*Golden Truth*) para calcular las métricas estadísticas del sistema (Accuracy, Precision, Recall).
*   `.env`: Archivo de secretos que contiene las credenciales de correo y variables de entorno del sistema (OLLAMA_HOST, API_URL).
*   `.gitignore`: Listado de exclusiones de Git para asegurar privacidad de datos y mantener el repositorio limpio.
*   `Dockerfile` y `docker-compose.yml`: Archivos de configuración de infraestructura (Fase 3) para contenerizar el backend, frontend y bases de datos.
*   `README.md`: Documento de presentación principal para desarrolladores y jurados.
*   `requirements.txt`: Inventario exacto de dependencias y librerías de Python.

---

## 📁 `data/` (Persistencia y Conocimiento)

Funciona como el disco duro físico del ecosistema. Todo su contenido está aislado mediante `.gitignore` debido a políticas de privacidad institucionales.

*   `01_raw_icesi/`: Repositorio de PDFs y documentos DOCX que contienen el perfil y capacidades de la Universidad Icesi.
*   `02_raw_secop/`: Archivos `.json` descargados de SECOP II. Funcionan como caché local para evitar saturar la SODA API.
*   `03_structured/`: (Reservado para futuras ingestas de datos tabulares limpios).
*   `04_outputs/`: Salidas y matrices de rendimiento. Contiene el `golden_truth.json` que utiliza `run_evaluation.py`.
*   `04_vector_db/`: Directorio autogestionado por **ChromaDB**. Es la memoria a largo plazo de SARA; almacena los vectores generados por el modelo BGE-M3.
*   `05_propuestas/`: Carpeta destino donde el Agente Redactor escribe los borradores de propuestas en formato Markdown (`.md`).
*   `historial_sara.sqlite3`: Base de datos transaccional relacional. Mantiene el historial auditable de todo contrato descargado, su viabilidad y justificación.

---

## 📁 `docs/` (Memoria Técnica y Académica)

Repositorio exclusivo para la generación documental del proyecto de grado. Contiene una extensa colección de artefactos organizados lógicamente:

**1. Manuales y Guías Técnicas:**
*   `MANUAL_DE_USUARIO_SARA.md`: Guía operativa para el usuario final (manejo de la interfaz visual).
*   `GUIA_DESPLIEGUE_SARA.md`: Instrucciones de ejecución en local (Nativo) y Producción (Docker).
*   `ESTRUCTURA_DIRECTORIOS_SARA.md`: Este mismo documento de arquitectura de carpetas.
*   `data_dictionary.md`: Estructura técnica de los datos.
*   `SODA_3_API.md`: Documentación de integración con Colombia Compra Eficiente.

**2. Artefactos Académicos y de Investigación:**
*   `PAPER_DRAFT_SARA.md` / `PAPER_SECTIONS_SARA.md`: Borradores oficiales del artículo académico.
*   `ACADEMIC_SUMMARY_SARA.md`: Resumen ejecutivo de la tesis.

**3. Diagramas y Especificaciones del Modelo:**
*   `ARQUITECTURA_SARA.md` / `DIAGRAMA_SARA.md`: Diagramas del ecosistema.
*   `METRICAS_EVOLUCION_SARA.md`: Benchmark histórico de precisión y falsos positivos.
*   `ESPECIFICACIONES_MODELOS.md`: Fichas técnicas de Meta Llama 3 (Q4) y BGE-M3.

**4. Reportes de Soporte:**
*   `smtp_policies.md`: Resolución histórica de bloqueos de correo.
*   *Otros insumos menores* (PDFs de políticas institucionales).

---

## 📁 `logs/` (Observabilidad)

Aislada de Git. Contiene los rastreos de depuración (salida estándar redirigida).

*   `api.log`: Registros de tráfico del backend FastAPI.
*   `frontend.log` / `streamlit.log`: Registros de conexión del panel de control.
*   `log_ingestion.txt`: Salida detallada de la vectorización de PDFs.
*   `ollama.log`: Trazabilidad de latencias y respuestas del motor Llama 3.
*   `pipeline_masivo.log`: Archivo consumido en tiempo real por el visor de Streamlit para mostrar qué hace el Worker Principal.

---

## 📁 `scripts/` (Ejecutables Utilitarios y Tareas Cron)

Archivos `.py` independientes que **se ejecutan por consola** (`python scripts/...`) para operaciones de mantenimiento y contingencia. Tienen inyectada lógica de `sys.path` para encontrar la carpeta `src/`.

*   `massive_ingestion.py`: Script pesado que barre `data/01_raw_icesi/`, procesa los documentos y reconstruye `ChromaDB` desde cero.
*   `force_evaluation.py`: Herramienta de inyección manual. Obliga a SARA a evaluar los contratos pendientes del *Golden Truth* sin afectar el historial normal diario.

---

## 📁 `src/` (El Motor: Lógica de Negocio Reutilizable)

El corazón de SARA. **Ningún archivo en esta carpeta se ejecuta por su cuenta**. Todos actúan como librerías internas que exponen Clases, Métodos y Modelos (MVC/Clean Architecture) para ser importados en la raíz o en los `scripts/`.

### 1. `src/agents/` (Personalidades IA)
Clases que representan entes autónomos con misiones específicas.
*   `matchmaker.py`: Agente de filtro inicial. Revisa los códigos UNSPSC y cruza palabras clave para descartar contratos ruidosos rápidamente.
*   `proposal_writer.py`: Agente Redactor. Toma una oportunidad de alta viabilidad y genera estructuralmente el borrador del documento técnico en lenguaje formal institucional.

### 2. `src/api/` (Endpoints)
Servicios de interconexión (Backend).
*   `main.py`: Código central de la API usando FastAPI. Provee rutas HTTP GET/POST para que el Frontend y otras aplicaciones consulten el estado de la base de datos `historial_sara.sqlite3`.

### 3. `src/brain/` (El Cerebro)
Capa de inferencia intensa y Recuperación Aumentada (RAG).
*   `critico_juridico.py`: Módulo especializado en buscar restricciones legales o cláusulas habilitantes (ej. multas, requerimientos de capital).
*   `llm_logic.py`: Interfaz de comunicación pura que envía el *prompt* hacia el servidor Ollama mediante HTTP.
*   `opportunity_evaluator.py`: Clase Maestra de la IA. Ensambla el flujo lógico: consulta a ChromaDB -> inserta en el Prompt -> invoca a Llama 3 -> procesa el JSON de respuesta.
*   `schemas.py`: Contiene plantillas Pydantic para garantizar que Llama 3 devuelva JSONs estructurados y sin alucinaciones.
*   `text_chunker.py`: Algoritmo semántico que divide textos largos de los PDFs en fragmentos (chunks) manejables conservando el solapamiento de palabras.
*   `vector_db.py`: Envoltorio (*wrapper*) alrededor de ChromaDB para facilitar la inserción de texto y la búsqueda por similitud vectorial usando *Embeddings*.

### 4. `src/evaluation/` (Analítica de Datos)
*   `metrics.py`: Modulo matemático. Calcula Matrices de Confusión, Accuracy, F1-Score y curvas lógicas basándose en resultados guardados en SQLite vs Golden Truth.

### 5. `src/frontend/` (Panel de Control Visual)
*   `app.py`: Módulo construido en Streamlit. Incluye los gráficos dinámicos (Altair), la lectura en tiempo real de `logs/pipeline_masivo.log` y el panel de configuración SMTP. Inicia todo el servidor web de cara al usuario final.

### 6. `src/ingestion/` (Buscadores y Extracción)
Librerías para conseguir datos del exterior.
*   `pdf_parser.py`: Clase que utiliza OCR y librerías especializadas para leer PDFs complejos e irregulares, devolviendo texto plano listo para ser vectorizado.
*   `soda_client.py`: Integración directa con SODA API de *Colombia Compra Eficiente*. Formatea las URLs y maneja la paginación y descargas JSON de los contratos de SECOP II.

### 7. `src/utils/` (Herramientas Transversales)
Funciones compartidas por múltiples módulos del ecosistema.
*   `db_manager.py`: Abstracción transaccional de SQLite. Se encarga de abrir conexiones, gestionar escrituras asíncronas y *upserts* en la tabla de `evaluaciones`.
*   `email_notifier.py`: Despachador SMTP. Genera tablas HTML estilizadas y envía alertas con los resultados de oportunidades viables a los interesados.

---
## 📁 `tests/` (Aseguramiento de Calidad)

Suite de scripts para verificación de integración y diagnóstico.

*   `test_smtp_debug.py`: Script de muy bajo nivel que simula una conexión `EHLO/TLS` directa para detectar si el servidor SMTP o el cortafuegos han bloqueado las IPs de SARA.

