# 📊 Diagrama Arquitectónico SARA (Flujo de Contrato)

## Opción 1: Diagrama de Texto Mejorado

```text
📥 [1. INGESTIÓN DE DATOS]
        │   • SODA Client extrae masivamente licitaciones de SECOP II (T-1).
        ▼
 🔍 [2. MOTOR RAG & CONTEXTO]
        │   • VectorDB (Chroma) recupera la memoria histórica y perfil de Icesi.
        │   • El modelo BGE-M3 vectoriza y alinea semánticamente los datos.
        ▼
 🧠 [3. COGNICIÓN MULTI-AGENTE (Llama 3 Local)]
        │   • Agente 1 (Explorador): Evalúa viabilidad Técnica y Financiera.
        │   • Agente 2 (Crítico): Audita estrictamente riesgos Legales y Jurídicos.
        ▼
 💾 [4. PERSISTENCIA & SÍNTESIS]
        │   • SQLite3 registra el 100% de los resultados para trazabilidad.
        │   • Si Viabilidad >= 70%: Agente 3 (Redactor) genera un borrador (.md).
        ▼
 📬 [5. DISTRIBUCIÓN & RESILIENCIA]
            • Email Notifier alerta a los stakeholders con el dictamen.
            • Sistema protegido por Circuit Breaker (Límites SMTP y Backlogs).
```

---

## Opción 2: Diagrama Visual (Mermaid)
*(Puedes copiar este código y pegarlo en [Mermaid Live Editor](https://mermaid.live/) para generar una imagen HD y usarla).*

```mermaid
graph TD
    %% Estilos de Nodos
    classDef ingestion fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
    classDef rag fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    classDef ai fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000
    classDef db fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
    classDef notif fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000

    %% Nodos
    A["📥 1. Ingestión (SECOP II) <br/> Cliente SODA API"]:::ingestion
    B["🔍 2. Motor RAG (BGE-M3) <br/> ChromaDB (Memoria Institucional)"]:::rag
    
    subgraph Cognición Multi-Agente (Llama 3 GPU)
        C["🧠 Agente Explorador <br/> (Viabilidad Técnica)"]:::ai
        D["⚖️ Agente Auditor <br/> (Filtro de Riesgos)"]:::ai
    end

    E{"¿Viabilidad >= 70%?"}:::db
    
    F["💾 Persistencia <br/> SQLite3 (100% del Historial)"]:::db
    G["📄 Agente Redactor <br/> Borrador de Propuesta (.md)"]:::ai
    H["📬 Notificación SMTP <br/> (Circuit Breaker Activado)"]:::notif

    %% Conexiones
    A -->|Datos Crudos| B
    B -->|Contexto Enriquecido| C
    C -->|Dictamen Inicial| D
    D -->|Dictamen Final| F
    F --> E
    
    E -- Sí --> G
    G --> H
    E -- No --> I((Fin del Flujo))
```
