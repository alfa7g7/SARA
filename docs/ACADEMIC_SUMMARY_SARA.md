# Resumen Técnico Estructurado para Artículo Científico: Proyecto SARA

Este documento sintetiza la arquitectura, tecnologías y paradigmas de ingeniería aplicados en el desarrollo de SARA (Sistema Automático de Rastreo y Análisis). Está redactado con rigor técnico para servir como insumo directo en la construcción del marco teórico, la metodología y los resultados del artículo académico.

---

## 1. Arquitectura Base Desacoplada
El núcleo transaccional del sistema se diseñó bajo un paradigma de microarquitectura modular, separando estrictamente la capa de control, el enrutamiento y la persistencia:
*   **FastAPI (Backend):** Actúa como el cerebro orquestador que expone endpoints RESTful de alto rendimiento (`/api/v1/opportunities`, `/api/v1/config`). FastAPI garantiza una comunicación asíncrona no bloqueante, ideal para manejar peticiones pesadas al LLM.
*   **Streamlit (Control Plane):** Proveé una interfaz de usuario (UI) reactiva orientada a la observabilidad de datos. Permite a los administradores visualizar grandes volúmenes de licitaciones utilizando componentes de diseño paramétrico (semáforos visuales) y *Live Logs* a través del secuestro de canales estándar (`stdout` vía `subprocess.Popen`) para depuración en vivo.
*   **SQLite3 con Migración Dinámica:** Elegido por su naturaleza embebida y portabilidad (Serverless DB). Implementamos un motor de migración de esquema dinámico en `db_manager.py` capaz de inyectar columnas (como `fecha_notificacion`) en tiempo de ejecución sin colapsar el sistema mediante el control estructurado de excepciones (`sqlite3.OperationalError`).

## 2. Pipeline RAG (Retrieval-Augmented Generation) y Memoria Institucional
Para mitigar la miopía de dominio intrínseca en los LLM genéricos, SARA incorpora una base de conocimiento fundamentada (RAG).
*   **ChromaDB (Vector Database):** Almacena representaciones vectoriales del perfil institucional de la universidad y contratos históricos (memoria).
*   **Modelo de Embeddings BGE-M3:** Elegido por su rendimiento estado-del-arte en semántica multilingüe. El pipeline vectoriza los documentos de SECOP II y calcula la similitud de coseno contra el perfil institucional, descartando el ruido sistémico (contratos no alineados) *antes* de que lleguen a la costosa ventana de contexto del LLM.

## 3. Ecosistema Multi-Agente y Abordaje Adversarial
El razonamiento del sistema no recae en un único prompt monolítico, sino en una arquitectura multi-agente determinista operando sobre **Meta Llama 3**:
*   **Agente Explorador:** Realiza la primera pasada cognitiva evaluando exclusivamente la viabilidad técnica y financiera de la licitación.
*   **Agente Crítico Jurídico:** Implementa un diseño *Adversarial* (contrapeso). Su única directiva es buscar fallos, riesgos legales y cláusulas restrictivas en el dictamen del Explorador. Si el Auditor Jurídico determina un alto riesgo, reduce drásticamente el puntaje de viabilidad. Este flujo dialéctico minimiza severamente las alucinaciones del modelo.
*   **Agente Redactor:** Actuando como un generador descendente, se activa únicamente si el consenso de los dos agentes anteriores supera el umbral de viabilidad (ej. 70%). Sistematiza los hallazgos redactando un borrador táctico en formato Markdown listo para la revisión humana.

## 4. Infraestructura y Aceleración Aislada (On-Premises)
A diferencia de arquitecturas dependientes de APIs comerciales (OpenAI, Anthropic), SARA fue diseñado bajo un estricto principio de soberanía y privacidad de datos (Zero Trust Cloud).
*   **Inferencia Local y Aceleración GPU:** Se ejecuta íntegramente de manera local utilizando Ollama como puente para la ejecución de pesos cuantizados de Llama 3. El entorno está puenteado directamente a la API CUDA de una GPU NVIDIA RTX 4070. Esto traslada la carga computacional intensiva (inferencia de tensores) de la CPU a los núcleos CUDA, logrando latencias de respuesta en milisegundos y procesando colas de licitaciones a cero costo marginal de nube.

## 5. Ingeniería de Resiliencia Operativa
Llevar la inteligencia artificial a entornos de producción requirió resolver fallos críticos en la infraestructura de distribución.
*   **Patrón Circuit Breaker en SMTP:** Para evitar que la IP del servidor sea listada en bases de *spam* por sobrepasar límites diarios (`5.4.5 Daily user sending limit exceeded`), se implementó un *Circuit Breaker*. El algoritmo monitoriza los códigos de error del proveedor de correo e interrumpe de inmediato (`raise/break` absoluto) el bucle de notificaciones ante cualquier fallo de cuota o red, evitando castigar al servidor externo con reintentos inútiles.
*   **Desacoplamiento de Estado para Backlog Management:** Al procesar meses de retraso histórico (miles de contratos), la validación original de cuotas diarias colapsaba. La arquitectura se refactorizó para aislar la variable temporal, creando el campo `fecha_notificacion` separado de la `fecha_evaluacion`. El timestamp se inyecta (`CURRENT_TIMESTAMP`) estrictamente en el instante del acuse de recibo del SMTP, lo que permite a SARA purgar pasivamente *backlogs* gigantes a un ritmo seguro (ej. 400 diarios) sin intervención humana.
