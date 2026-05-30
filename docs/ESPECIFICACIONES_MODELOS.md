# 🧠 Especificaciones Técnicas de Modelos IA (SARA)

Este documento detalla las características técnicas de los dos modelos fundamentales que operan en la arquitectura de SARA. Está diseñado para proveer los argumentos exactos (*Discurso Clave*) que justifican estas decisiones de diseño durante la sustentación.

---

## 1. Motor de Inferencia y Generación: Meta Llama 3

Este es el cerebro cognitivo principal (la "G" en RAG - *Generation*). Se encarga de evaluar, razonar y redactar los dictámenes basándose en el contexto recuperado.

### 📊 Especificaciones Técnicas
*   **Modelo Base:** Meta Llama 3 (Versión *Instruct*).
*   **Cantidad de Parámetros:** **8.0B** (8 Billones de parámetros).
*   **Peso de Almacenamiento (Size):** **4.7 GB** (4,661,224,676 bytes).
*   **Nivel de Cuantización:** **Q4_0** (Cuantizado a 4-bits en formato GGUF).

### 💡 Discurso Clave (Defensa Técnica)
> *"Para el razonamiento cognitivo, implementamos el modelo Meta Llama 3 de 8 Billones de parámetros. Para lograr inferencia local de altísima velocidad sin depender de la nube, aplicamos una técnica de **cuantización a 4-bits (Q4_0)**. Esto comprimió el peso del modelo a solo **4.7 GB**, permitiendo que quepa holgadamente en la VRAM de nuestra NVIDIA RTX 4070 (que cuenta con 12GB). Esto nos deja más de 7GB libres de memoria de video dedicados exclusivamente a procesar ventanas de contexto larguísimas (pliegos de condiciones enteros), garantizando una latencia bajísima (~450ms) sin que el sistema colapse por falta de memoria (Out-of-Memory)."*

---

## 2. Motor de Vectorización (Embeddings): BAAI BGE-M3

Este es el motor semántico (la "R" en RAG - *Retrieval*). Se encarga de convertir tanto el perfil de la universidad como los pliegos de SECOP en vectores matemáticos para que ChromaDB pueda encontrar similitudes.

### 📊 Especificaciones Técnicas
*   **Creador:** BAAI (*Beijing Academy of Artificial Intelligence*).
*   **Cantidad de Parámetros:** **567 Millones** (0.57B). Liviano y altamente optimizado.
*   **Dimensiones del Vector:** **1024 dimensiones** (coordenadas matemáticas por cada texto).
*   **Ventana de Contexto (Max Input):** **8,192 tokens**.

### 💡 Discurso Clave (Defensa Técnica)
> *"Elegimos BGE-M3 como nuestro motor de vectorización por sus capacidades **'3M'**:* 
> 1.  ***Multi-Lingualidad:** Entiende más de 100 idiomas, vital para especificaciones técnicas extranjeras incrustadas en contratos de SECOP.*
> 2.  ***Multi-Granularidad:** Su enorme ventana de contexto de **8,192 tokens** le permite procesar desde una frase corta hasta un pliego extenso con la misma precisión.*
> 3.  ***Multi-Funcionalidad:** Soporta búsqueda densa (semántica pura) y búsqueda dispersa (palabras clave exactas), garantizando que ChromaDB recupere la memoria institucional de Icesi con precisión quirúrgica.*
> 
> *Frente a opciones comerciales como OpenAI, optamos por BGE-M3 porque es **Open Source**, opera localmente protegiendo la confidencialidad estratégica de la Universidad, y en los benchmarks actuales (MTEB) supera a modelos cerrados en tareas de recuperación ocupando menos de 2.5 GB en memoria."*
