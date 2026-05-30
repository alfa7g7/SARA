import os
import sqlite3
import httpx
from fastapi import FastAPI, Body, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional
from src.brain.opportunity_evaluator import OpportunityEvaluator
from src.utils.db_manager import get_db_connection, get_config, update_config

app = FastAPI(
    title="SARA API",
    description="API REST base para SARA Web y Panel Administrativo",
    version="1.0.0"
)

# Configuración de CORS permitiendo todos los orígenes (*)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health")
async def health_check():
    """
    Endpoint de estado (Health Check) proactivo.
    Verifica SQLite y Llama 3 (Ollama).
    """
    db_ok = False
    try:
        conn = get_db_connection()
        conn.close()
        db_ok = True
    except Exception:
        pass
        
    ollama_ok = False
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            ollama_url = os.getenv("OLLAMA_HOST", "http://localhost:11434")
            resp = await client.get(f"{ollama_url}/")
            if resp.status_code == 200:
                ollama_ok = True
    except Exception:
        pass

    return {
        "status": "OK" if db_ok and ollama_ok else "DEGRADED",
        "database_connected": db_ok,
        "ollama_connected": ollama_ok
    }

@app.get("/api/v1/config")
async def read_sara_config():
    """Lee la configuración dinámica desde SQLite."""
    return get_config()

@app.put("/api/v1/config")
async def write_sara_config(updates: Dict[str, Any] = Body(...)):
    """Actualiza la configuración en la base de datos."""
    update_config(updates)
    return {"status": "success", "message": "Configuración actualizada correctamente"}

@app.get("/api/v1/opportunities")
async def get_opportunities(
    min_viabilidad: Optional[int] = Query(None, description="Filtrar por viabilidad mínima"),
    fecha: Optional[str] = Query(None, description="Filtrar por fecha exacta (YYYY-MM-DD)"),
    limit: Optional[int] = Query(5000, description="Límite máximo de registros a devolver")
):
    """
    Endpoint de consumo para Empleados/Streamlit.
    Consulta el historial de SQLite y permite filtrado dinámico sin truncar a la fuerza.
    """
    if min_viabilidad is None:
        config = get_config()
        min_viabilidad = int(config.get("umbral_pantalla", 70))

    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = "SELECT * FROM evaluaciones WHERE viabilidad >= ?"
    params = [min_viabilidad]
    
    if fecha:
        query += " AND date(fecha_evaluacion) = ?"
        params.append(fecha)
        
    query += " ORDER BY viabilidad DESC, fecha_evaluacion DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return rows

@app.post("/api/v1/evaluate_opportunity")
async def evaluate_opportunity(secop_record: Dict[str, Any] = Body(..., description="JSON completo del proceso SECOP II (20 campos)")):
    """
    Endpoint para evaluar oportunidades del SECOP II usando Llama 3 y RAG de forma manual.
    Recibe el JSON completo de la licitación y devuelve el porcentaje de viabilidad.
    """
    print(f"\n[API] Solicitud de evaluación manual recibida para ID: {secop_record.get('id_del_proceso', 'Desconocido')}")
    
    # Directorio de persistencia DB 
    db_path = os.path.join(os.getcwd(), "data", "04_vector_db") 
    
    evaluator = OpportunityEvaluator(vector_db_dir=db_path)
    evaluacion = evaluator.evaluate_secop_opportunity(secop_record)
    
    return evaluacion
