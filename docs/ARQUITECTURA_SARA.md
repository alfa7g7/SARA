# 🖥️ Diagrama de Arquitectura de Software SARA

Este es el diagrama estructural de los componentes de software de SARA. Muestra cómo se conectan las tecnologías a nivel de infraestructura, las cuales están desplegadas como **microservicios independientes usando Docker Compose**.

---

## Opción 1: Diagrama de Texto Mejorado (Para copiar y pegar)


```text
 ☁️ [DATOS EXTERNOS]                   🖥️ [CAPA DE PRESENTACIÓN]
        │                                        │
        ▼                                        ▼
 🔌 [1. SODA Client] ──────────────────►  📊 [Streamlit UI] (Control Plane)
 (Extracción T-1 SECOP II)                 │   │ (Peticiones REST)
        │                                  │   ▼
        │    (JSON)                        │  ⚙️ [FastAPI Backend] (Orquestador Central)
        │                                  │   │
        ▼                                  │   │
 🧠 [2. Motor Cognitivo] ◄────────────────┘   │ (Live Logs / Estado en tiempo real)
 (Llama 3 + ChromaDB BGE-M3)                   │
        │                                      │
        │    (Dictamen + Propuesta)            ▼
        │                                 💾 [3. Persistencia de Datos]
        ▼                                 (SQLite3 Transaccional / Migraciones Dinámicas)
 📧 [4. Distribución]
 (Servidor SMTP con Circuit Breaker)
```

---

## Opción 2: Diagrama Visual (Mermaid)
*(Puedes copiar este bloque y pegarlo en [Mermaid Live Editor](https://mermaid.live/) para generar la imagen HD y usarla).*

```mermaid
graph LR
    %% Estilos de Nodos
    classDef cloud fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
    classDef backend fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000
    classDef frontend fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000
    classDef db fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
    classDef engine fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000

    %% Fuentes Externas
    SECOP(("☁️ SECOP II <br/> (Datos Públicos)")):::cloud
    SMTP(("📧 Servidor SMTP <br/> (Distribución)")):::cloud

    %% Frontend (Control Plane)
    subgraph Capa_UI ["Capa de Presentación & Observabilidad"]
        UI["🖥️ Streamlit Frontend <br/> (Control Plane)"]:::frontend
        Logs>["Live Logs Popen <br/> (Modo Debug)"]:::frontend
    end

    %% Backend (Orquestador)
    subgraph Capa_Backend ["Núcleo Central"]
        API["⚙️ FastAPI Backend <br/> (Enrutamiento & API)"]:::backend
        SODA["🔌 SODA Client <br/> (Ingesta Diaria T-1)"]:::backend
    end

    %% Persistencia
    subgraph Capa_Datos ["Capa de Persistencia"]
        SQL[("💾 SQLite3 <br/> (Migración Dinámica)")]:::db
    end

    %% Motor LLM/RAG (Aisaldo conceptualmente para slide 3)
    LLM_Engine[["🧠 Motor Cognitivo <br/> (Agentes Llama 3 + ChromaDB)"]]:::engine

    %% Relaciones / Integraciones
    SECOP --"Extracción JSON"--> SODA
    SODA --> API
    
    UI --"Peticiones REST"--> API
    API --"Estado en tiempo real"--> Logs
    UI -.-> Logs

    API --"CRUD Transaccional"--> SQL
    API <--"Evaluar Licitación"--> LLM_Engine
    
    LLM_Engine -.->|"Si Viabilidad >= 70% <br/> (Circuit Breaker)"| SMTP
```

### 💡 Por qué este diagrama es perfecto:
*   **Separación de Responsabilidades:** Muestra claramente la separación entre la *Capa UI* (Streamlit), el *Núcleo* (FastAPI/SODA) y la *Persistencia* (SQLite).
*   **Agnosticismo del Motor LLM:** Aquí el motor cognitivo aparece como una única "caja negra" conectada a FastAPI, manteniendo el enfoque en la *Ingeniería de Software* clásica.
*   **Flujo de Izquierda a Derecha:** Es muy natural de leer. Los datos entran por la izquierda (SECOP), pasan por el backend, se guardan abajo y se controlan desde arriba.
