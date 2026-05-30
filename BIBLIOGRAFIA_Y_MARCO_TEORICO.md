# Bibliografía y Marco Teórico de Referencia: Proyecto SARA

Este documento establece el marco teórico, metodológico y tecnológico base para la arquitectura de SARA (Sistema de Análisis mediante RAG y Agentes). Sirve como guía de estudio para comprender los componentes desarrollados a lo largo de todas las fases del proyecto y proporciona referencias bibliográficas para trabajos futuros.

## 1. Procesamiento de Lenguaje Natural (NLP) y Recuperación (RAG)
*   **Fundamentos RAG:** Arquitecturas de Generación Aumentada por Recuperación (*Retrieval-Augmented Generation*).
*   **Bases de Datos Vectoriales:** Uso de **ChromaDB** para el almacenamiento, indexación y recuperación eficiente de vectores (*Similarity Search* y *Top-K Retrieval*).
*   **Modelos de Embeddings (State-of-the-Art):** Arquitectura del modelo **BAAI/bge-m3** (Beijing Academy of Artificial Intelligence). Capacidades "3M" (Multi-Lingual, Multi-Granular, Multi-Funcional) en tareas de recuperación semántica densa y dispersa.
*   **Ingeniería de Textos:** Estrategias avanzadas de *Chunking* semántico y particionamiento con superposición (*overlap*) estructurado.

## 2. Inferencia Cognitiva y Sistemas Multi-Agente
*   **Modelos Locales y Eficiencia:** Arquitectura de **Meta Llama 3 (8B)**.
*   **Cuantización de Redes Neuronales:** Técnicas de compresión GGUF (Específicamente **Q4_0** a 4-bits) para inferencia local de alta velocidad en GPUs de memoria limitada (NVIDIA RTX 4070) previniendo desbordamientos (*Out-of-Memory*).
*   **Orquestación Multi-Agente (Paradigma Adversarial):** Flujos de debate entre agentes. Implementación de Agentes Exploradores y Agentes Auditores Jurídicos para reducir dramáticamente las alucinaciones del LLM y el sesgo de complacencia (*Sycophancy*).
*   **Structured Output:** Inyección de esquemas JSON estrictos para obligar a modelos generativos a devolver estructuras de datos deterministas predecibles.

## 3. Ingeniería de Software y Resiliencia Sistémica
*   **Arquitecturas de Ingestión (Pipelines de Datos):** Extracción automatizada (Zero-Touch) desde plataformas gubernamentales usando la especificación **SODA API** (Socrata Open Data API) de SECOP II.
*   **Desarrollo Backend API REST:** **FastAPI** para enrutamiento asíncrono y **Pydantic** para la serialización y validación estricta de dominios de datos.
*   **Patrones de Resiliencia:** Implementación del patrón de diseño **Circuit Breaker** para la tolerancia a fallos en servicios externos (ej. Límites de cuota SMTP diarios).
*   **Persistencia Transaccional:** Uso de **SQLite3** con manejo dinámico de esquemas y aislamiento de procesos paralelos para un *Burn-in Test* sin bloqueos de base de datos.
*   **Control Plane y Observabilidad:** Uso de **Streamlit** para *dashboards* de analítica visual y lectura de *Live Logs* para monitoreo de subprocesos.
*   **Contenerización y Orquestación:** Preparación de la arquitectura hacia un modelo Cloud-Native mediante **Docker**, aislando servicios cognitivos de servicios transaccionales.

## 4. MLOps y Métricas de Evaluación Continua
*   **Benchmarking y Métricas Clasificatorias:** Medición empírica en el dominio de licitaciones utilizando Error Absoluto Medio (MAE), Precisión, Exhaustividad (Recall) y F1-Score.
*   **Ciclos de Retroalimentación (Human-in-the-loop):** Diseño e implementación del módulo **Golden Truth**.
*   **Evaluación de Modelos en Producción:** Comprensión de la "Brecha de Generalización" (*Distribution Shift*) al pasar de un conjunto de evaluación cerrado a un entorno *Out-of-distribution* en caliente (*Burn-in Test*), y el uso del re-entrenamiento pasivo de la memoria institucional sin recurrir a un *Fine-tuning* paramétrico.

---

## 📚 Referencias Bibliográficas Recomendadas (Para Estudio e Investigación)

1.  **Sobre RAG y Embeddings:**
    *   Chen, J., et al. (2024). *BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation*. Beijing Academy of Artificial Intelligence.
    *   Lewis, P., et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. NeurIPS.
2.  **Sobre Modelos Multi-Agente y Cuantización:**
    *   Meta AI. (2024). *The Llama 3 Herd of Models*.
    *   Dettmers, T., et al. (2022). *LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale*. (Conceptos base de cuantización para inferencia).
    *   Chan, C., et al. (2023). *ChatEval: Towards Better LLM-based Evaluators through Multi-Agent Debate*. (Sustento académico para nuestro Agente Auditor).
3.  **Sobre Resiliencia de Software (Circuit Breaker):**
    *   Nygard, M. T. (2018). *Release It! Design and Deploy Production-Ready Software*. Pragmatic Bookshelf. (Capítulo sobre Patrón Circuit Breaker).
4.  **Sobre MLOps y Human-in-the-Loop:**
    *   Kreuzberger, D., et al. (2023). *Machine Learning Operations (MLOps): Overview, Definition, and Architecture*. IEEE Access.
    *   Wu, T., et al. (2022). *A Survey of Human-in-the-loop for Machine Learning*.
