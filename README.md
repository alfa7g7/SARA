___________________________________________________________________________________

# SARA - Sistema de Análisis mediante RAG y Agentes

Este proyecto es parte del curso **Proyecto III de innovación tecnológica de IA** de la Maestría en Inteligencia Artificial aplicada de la Universidad Icesi, Cali Colombia.

#### -- Estado del Proyecto: [Completado / Listo para Sustentación]

## Miembros y Contribuyentes

**Líder del Proyecto: [Fabian Salazar Figueroa](https://github.com/alfa7g7) | <fabian.salazarfigueroa77@gmail.com>**

**Docente / Tutor: [José Armando Ordoñez](https://github.com/armandoordonez)**

#### Otros Miembros Integrantes

|Name     |  Email   |
|---------|-----------------|
|[Luis Esteban Ordoñez Erazo](https://github.com/leoe21)|   <esteban.leoe@gmail.com>        |
|[Raul Albero Echeverry Lopez](https://github.com/RaulEcheverryLopez)   |   <raelv06@gmail.com>    |
|[Arlex Pino Aguirre](https://github.com/arlexpin)|   <apino@icesi.edu.co>   |
|[Alfredo Aponte](https://github.com/ajapontes)|   <alfredo.aponte@u.icesi.edu.co>   |

## Contacto

* ¡No dudes en contactar al líder del equipo si tienes alguna pregunta o si estás interesado en colaborar con el proyecto!

## Introducción y Objetivos del Proyecto

El objetivo principal de SARA es resolver la ineficiencia y el error humano en la búsqueda y evaluación manual de licitaciones públicas del Estado colombiano (SECOP II). SARA es un ecosistema autónomo basado en Inteligencia Artificial que ingesta masivamente pliegos de condiciones, los cruza semánticamente con las capacidades institucionales de la Universidad Icesi mediante una arquitectura RAG, y utiliza un panel Multi-Agente (Llama 3) para emitir un dictamen de viabilidad, alertando a los *stakeholders* y redactando borradores de propuesta de forma automatizada.

### Aliado / Beneficiario Principal

* **Universidad Icesi** (Dirección de Consultoría y Extensión)
* Sitio web: [www.icesi.edu.co](https://www.icesi.edu.co)

### Metodologías Implementadas

* Generación Aumentada por Recuperación (RAG)
* Orquestación Multi-Agente (*Adversarial Debate*)
* Procesamiento de Lenguaje Natural (NLP)
* MLOps & Mejora Continua (*Human-in-the-loop / Golden Truth*)
* Ingeniería de Resiliencia (*Circuit Breaker Pattern*)
* Evaluaciones de Similitud Semántica Vectorial

### Stack Tecnológico

* **Python 3** (Ecosistema base)
* **LLM Local:** Meta Llama 3 8B (Cuantización Q4_0 vía Ollama)
* **Embeddings:** BAAI BGE-M3
* **Bases de Datos:** ChromaDB (Vectorial), SQLite3 (Relacional/Transaccional)
* **Backend & API:** FastAPI, Pydantic, SODA API Client
* **Frontend / UI:** Streamlit
* **Infraestructura:** Docker & Docker Compose

## Descripción del Proyecto

El proyecto SARA aborda un desafío crítico: la Universidad Icesi dejaba pasar oportunidades de negocio o incurría en riesgos legales ocultos por no tener capacidad humana para procesar miles de pliegos diarios en SECOP II. 

Para resolverlo, construimos una solución integral de **Software Engineering + AI**:
1. **Ingesta Autónoma:** Un cliente automatizado extrae la data diaria mediante la API pública de SODA.
2. **Memoria RAG:** El texto es vectorizado por el modelo multilingüe `BGE-M3` y almacenado en `ChromaDB`, donde SARA busca si el perfil de la universidad hace *"match"* con la licitación.
3. **Cognición Adversarial:** Un *Agente Explorador* aprueba técnicamente la propuesta, y un *Agente Auditor Jurídico* intenta buscar activamente fallos legales o trampas en los pliegos para evitar falsos positivos. 
4. **Notificación Inteligente:** Si la viabilidad es alta (>70%), SARA usa un patrón de *Circuit Breaker* para enviar notificaciones SMTP de manera resiliente, adjuntando un borrador en *Markdown* redactado por un tercer agente especializado.

*Desafíos superados:* SARA resolvió problemas de latencia (reducción del 94% implementando aceleración GPU) y problemas de *sycophancy* en el LLM (el sesgo de ser excesivamente complaciente) mediante su diseño de debate entre agentes.

> ⚠️ **Aviso de Privacidad y Protección de Datos:**
> Debido a las políticas de privacidad de la Universidad Icesi y la confidencialidad estratégica de su perfil institucional, **no se subirá ni compartirá la base de datos vectorial (ChromaDB) ni la base de datos transaccional (SQLite3)** en este repositorio público. Todo el directorio `data/` (incluyendo `data/04_vector_db/` y `sara_database.db`) ha sido añadido al `.gitignore`. Los investigadores que deseen replicar el sistema deberán construir su propia base de conocimiento institucional mediante el pipeline de ingesta.

## Estructura del Proyecto

El repositorio está organizado bajo principios de modularidad y arquitectura limpia:

```text
SARA/
├── data/                 # Ignorado en Git (Bases de datos, Vectores, PDFs)
├── docs/                 # Documentación, diagramas y papers de referencia
├── logs/                 # Registros de observabilidad en tiempo real (.log)
├── scripts/              # Herramientas de mantenimiento y ejecución manual (scripts)
├── src/                  # Código fuente central
│   ├── agents/           # Lógica de los Agentes (Explorador, Auditor, Redactor)
│   ├── api/              # Capa de servicios REST (FastAPI)
│   ├── brain/            # Orquestación del motor LLM (Ollama)
│   ├── evaluation/       # Algoritmos de validación y cálculo de métricas
│   ├── frontend/         # Panel de control e interfaz de observabilidad (Streamlit)
│   └── ingestion/        # Scripts para interactuar con SODA API y vectorizar
├── tests/                # Batería de pruebas unitarias y de integración
├── run_pipeline.py       # Orquestador principal (CLI)
└── run_evaluation.py     # Script para calcular métricas contra el Golden Truth
```

## Guía de Instalación y Ejecución (Getting Started)

Existen dos maneras de desplegar el ecosistema SARA: Instalación Local o mediante Contenedores (Docker).

### Opción A: Despliegue Local (Desarrollo)

1. Clonar este repositorio.
2. Crear un entorno virtual e instalar dependencias:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Instalar Ollama y descargar el modelo exacto (Llama 3 8B) localmente:
   ```bash
   ollama pull llama3:8b
   ```
4. **Ejecutar la Interfaz de Observabilidad (Frontend):**
   ```bash
   streamlit run src/frontend/app.py
   ```
5. **Ejecutar el Pipeline Core (Backend):**
   ```bash
   python run_pipeline.py --limit 50 --date 2024-05-27
   ```

### Opción B: Despliegue con Docker (Producción)

Para garantizar la portabilidad y evitar conflictos de dependencias, SARA está diseñado para ejecutarse sobre una infraestructura de microservicios. 
Asegúrate de tener instalado `Docker`, `Docker Compose v2`, y el paquete **NVIDIA Container Toolkit** en tu servidor host para permitir que el contenedor de Ollama detecte tu GPU.

1. Construir y levantar la orquesta (4 servicios: API, UI, Worker, Ollama):
   ```bash
   docker-compose up --build -d
   ```
2. Acceder a los servicios:
   * **API de SARA (FastAPI):** `http://localhost:8000/docs`
   * **Panel de Control (Streamlit):** `http://localhost:8501`
   * **SARA Worker:** Corre silenciosamente en background (`docker logs -f sara_worker`).

---

## Entregables y Artefactos del Proyecto

Toda la fundamentación teórica, de métricas y arquitectónica está disponible en los documentos internos del repositorio:

* [Diagrama de Arquitectura de Software](docs/ARQUITECTURA_SARA.md)
* [Flujo Lógico Multi-Agente](docs/DIAGRAMA_SARA.md)
* [Evolución de Métricas y Benchmark](docs/METRICAS_EVOLUCION_SARA.md)
* [Especificaciones de Modelos (Llama3 y BGE-M3)](docs/ESPECIFICACIONES_MODELOS.md)
* [Marco Teórico y Bibliografía](BIBLIOGRAFIA_Y_MARCO_TEORICO.md)
* [Estructura Completa de Directorios](docs/ESTRUCTURA_DIRECTORIOS_SARA.md)
* [Guía de Despliegue y Ejecución](docs/GUIA_DESPLIEGUE_SARA.md)
* [Manual de Usuario SARA](docs/MANUAL_DE_USUARIO_SARA.md)
