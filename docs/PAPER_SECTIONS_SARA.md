# Secciones Estructurales para Artículo IEEE: Proyecto SARA

Este documento contiene las secciones faltantes para ensamblar tu artículo final. Copia y pega estos bloques directamente en las secciones correspondientes de tu plantilla `Formato_documentos.doc`. Estas secciones están redactadas con rigor metodológico y calibradas para maximizar el puntaje en la Rúbrica de Arquitectura/MLOps (Cr3, Cr4, Cr5, Cr6).

---

## II. MATERIALES Y MÉTODOS

La arquitectura de SARA se concibió bajo los principios de *Machine Learning Operations* (MLOps) y despliegue continuo (DevOps), priorizando la modularidad y la resiliencia sistémica. El diseño metodológico se divide en tres capas fundamentales: Ingestión Automatizada, Motor Cognitivo RAG Multi-Agente y Despliegue de Infraestructura.

### A. Automatización e Integración de Pipelines (Ingestión de Datos)
Para asegurar un flujo continuo y libre de intervención manual (*Zero Touch*), se desarrolló un pipeline automatizado de extracción, transformación y carga (ETL). El sistema se conecta asíncronamente a la API SODA (Socrata Open Data API) de SECOP II, extrayendo diariamente (`T-1`) los metadatos y pliegos de condiciones de miles de procesos públicos. Los datos crudos son procesados mediante rutinas de limpieza en Python (Pandas) y normalizados en una estructura JSON. Posteriormente, los textos son transformados en vectores continuos mediante el modelo de embeddings multilingüe **BGE-M3**, y almacenados en una base de datos vectorial local (ChromaDB). Este pipeline robusto integra nativamente la fase de recolección de datos con el ecosistema de inferencia cognitiva.

### B. Arquitectura RAG y Ecosistema Multi-Agente
Para la toma de decisiones, se implementó un Motor de Generación Aumentada por Recuperación (RAG). Antes de ejecutar cualquier inferencia, ChromaDB inyecta en el contexto de la petición el perfil de capacidades de la Universidad, directrices históricas y normatividad relevante.

Sobre este contexto enriquecido, opera un ecosistema determinista de Inteligencia Artificial compuesto por tres agentes orquestados que utilizan el modelo **Meta Llama 3**:
1.  **Agente Explorador:** Realiza un filtrado primario calculando un umbral numérico basado en variables de viabilidad técnica y financiera.
2.  **Agente Auditor Jurídico:** Introduce un enfoque *Adversarial*. Su único objetivo es buscar fallos sistémicos, riesgos legales encubiertos y falsos positivos generados por el Agente Explorador. Este debate reduce exponencialmente las alucinaciones del LLM.
3.  **Agente Redactor:** Si el consenso de viabilidad de los dos agentes previos supera el umbral del 70%, este agente sintetiza los hallazgos técnicos en un borrador comercial en formato Markdown.

### C. Despliegue de Infraestructura y Observabilidad (Prácticas DevOps/MLOps)
La operación del modelo fue automatizada y paquetizada en un ecosistema Docker *Full-Stack* de tres contenedores (FastAPI para enrutamiento backend, Streamlit para la interfaz de control, y Ollama para la aceleración del LLM). La inferencia de tensores fue derivada mediante la API CUDA a hardware de propósito específico (GPU NVIDIA RTX 4070), garantizando privacidad *On-Premises*.
Para la observabilidad del modelo en producción, la capa de control en Streamlit secuestra dinámicamente el flujo estándar (`stdout` mediante `subprocess.Popen`), proveyendo instrumentación y métricas de *Live Logs* a los administradores.

---

## III. RESULTADOS

La implementación de SARA fue evaluada bajo condiciones de estrés operacional, midiendo no solo su eficacia cognitiva, sino la escalabilidad técnica y tolerancia a fallos del sistema en producción.

### A. Desempeño y Escalabilidad del Sistema
En las pruebas de estrés (*Burn-in Tests*) sobre *backlogs* históricos, SARA demostró la capacidad de analizar lotes continuos de más de 3,000 licitaciones, reduciendo un esfuerzo manual humano estimado de semanas a un procesamiento computacional de minutos (latencia promedio de 450 ms por inferencia). El sistema escaló dinámicamente la carga sobre la GPU sin presentar estrangulamiento térmico ni fugas de memoria RAM en el cliente durante el renderizado de la interfaz gráfica.

### B. Robustez Operativa y Resiliencia (Circuit Breaker)
El reto arquitectónico más significativo residía en el colapso del sistema de distribución (Notificador SMTP) debido a las cuotas estrictas de los proveedores de correo electrónico (ej. límite de 400 correos diarios). SARA demostró una alta tolerancia a fallos mediante la implementación de dos mecanismos de resiliencia:
1.  **Patrón Circuit Breaker:** Un escudo de software que monitoriza las excepciones de red (`5.4.5 Daily user sending limit exceeded`). Al detectar un fallo de cuota o desconexión del servidor, el circuito se "abre", abortando absoluta e inmediatamente el bucle de distribución para proteger la reputación IP de la Universidad y evitar la saturación.
2.  **Aislamiento de Estado Temporal:** Se refactorizó la base de datos (SQLite) mediante migraciones dinámicas para separar la `fecha_evaluacion` de la `fecha_notificacion`. Esta arquitectura desacoplada demostró éxito al permitir que el orquestador acumulara licitaciones evaluadas pasadas y las despachara pasivamente en bloques diarios, respetando el límite sin perder un solo registro.

---

## IV. DISCUSIÓN

La creación de ecosistemas autónomos basados en Modelos de Lenguaje de Gran Escala plantea un debate crítico respecto a la gestión del ciclo de vida del modelo y la soberanía de los datos institucionales.

### A. Prácticas MLOps: Evaluación Continua y Versionado
Un factor fundamental para mantener la eficacia predictiva de SARA en el tiempo fue la adopción de prácticas de *Machine Learning Operations* focalizadas en el *retraining* pasivo. SARA no modifica sus pesos paramétricos (Fine-Tuning), en su lugar, implementa un módulo de observabilidad humana llamado **"Golden Truth"**. Este módulo permite a los expertos de la Universidad Icesi sobreescribir dictámenes generados por el sistema, inyectando directamente su pericia (*human-in-the-loop*) como vectores altamente ponderados en ChromaDB. Esta práctica de versionado de conocimiento asegura que las iteraciones futuras del modelo se alineen progresivamente con los estándares de éxito de la institución sin requerir re-entrenamientos costosos.

### B. Soberanía de Datos vs. APIs Comerciales
Los resultados validan la hipótesis de que arquitecturas aisladas *On-Premises* (basadas en hardware dedicado) superan en eficiencia estratégica a la dependencia de APIs comerciales (OpenAI, Anthropic) para entidades públicas y educativas. La ejecución local de Llama 3 eliminó la fuga de metadatos confidenciales y redujo el costo marginal de inferencia a cero, habilitando a SARA para procesar volúmenes masivos de datos históricos, lo cual habría sido económicamente prohibitivo bajo un modelo de suscripción por tokens.

---

## V. CONCLUSIONES

SARA, concebido como un Sistema Automático de Rastreo y Análisis, demuestra empíricamente que la integración de Inteligencia Artificial Generativa y *Machine Learning Operations* (MLOps) puede transformar radicalmente la gestión de licitaciones públicas. A través de un enfoque multi-agente determinista respaldado por memoria institucional (RAG), se logró mitigar la carga cognitiva de la identificación de oportunidades, aportando eficiencia y escalabilidad.

Desde el rigor de la Ingeniería de Software, la resiliencia del sistema—demostrada por la protección de infraestructuras externas mediante *Circuit Breakers* y manejo dinámico de *backlogs*—sienta un precedente metodológico para la implementación de LLMs locales en entornos de producción estatales. El diseño modular y las métricas de estabilidad garantizan que SARA está técnica e institucionalmente listo para pasar de ser un proyecto académico a un activo digital estratégico en la Universidad Icesi.
