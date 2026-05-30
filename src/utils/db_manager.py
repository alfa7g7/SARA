import sqlite3
import os
import json

# ESQUEMA MAESTRO DINÁMICO
# Si deseas agregar una columna a SARA en el futuro, agrégala aquí y el sistema 
# migrará la base de datos automáticamente en su próxima ejecución.
SCHEMA = {
    "id_proceso": "TEXT UNIQUE",
    "entidad": "TEXT",
    "objeto": "TEXT",
    "viabilidad": "INTEGER",
    "justificacion": "TEXT",
    "fecha_evaluacion": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    "notificado": "INTEGER DEFAULT 0",
    "fecha_notificacion": "DATETIME DEFAULT NULL",
    "referencia": "TEXT DEFAULT ''",
    "url": "TEXT DEFAULT ''"
}

DEFAULT_CONFIG = {
    "umbral_pantalla": "70",
    "umbral_correo": "70",
    "destinatarios_notificacion": '["raul.echeverry@u.icesi.edu.co", "fabian.salazar@u.icesi.edu.co", "alfa7g7@gmail.com"]',
    "max_emails_per_run": "400",
    "blacklist_palabras": "[]",
    "auditor_estricto": "true"
}

def get_db_connection(db_path="data/historial_sara.sqlite3"):
    """
    Obtiene una conexión a la base de datos y garantiza que el esquema
    y todas sus columnas estén actualizados dinámicamente según SCHEMA.
    """
    abs_path = os.path.join(os.getcwd(), db_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    
    # Timeout alto y modo WAL para prevenir colisiones de escritura (Database is locked)
    conn = sqlite3.connect(abs_path, timeout=30.0)
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA synchronous=NORMAL;")
    
    # 1. Creación Inicial (Si la tabla no existe)
    columns_def = ", ".join([f"{col} {dtype}" for col, dtype in SCHEMA.items()])
    cursor.execute(f"CREATE TABLE IF NOT EXISTS evaluaciones ({columns_def})")
    
    # 2. Migración de Esquema Dinámica (Para DBs antiguas)
    cursor.execute("PRAGMA table_info(evaluaciones)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    
    for col_name, dtype in SCHEMA.items():
        if col_name not in existing_columns:
            # Limpiar constraints incompatibles con ALTER TABLE en SQLite
            clean_dtype = dtype.replace(" UNIQUE", "").replace(" PRIMARY KEY", "")
            try:
                cursor.execute(f"ALTER TABLE evaluaciones ADD COLUMN {col_name} {clean_dtype}")
                print(f"🔧 [DB Manager] Columna inyectada automáticamente en SQLite: {col_name}")
            except sqlite3.OperationalError as e:
                print(f"⚠️ [DB Manager] OperationalError (columna {col_name} probablemente ya existe): {e}")
            except Exception as e:
                print(f"❌ [DB Manager] Error inyectando columna {col_name}: {e}")
                
    # 3. Módulo de Configuración Dinámica (Llave-Valor)
    cursor.execute("CREATE TABLE IF NOT EXISTS configuracion (clave TEXT PRIMARY KEY, valor TEXT)")
    
    # Inyectar defaults (Clean Slate) si la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM configuracion")
    if cursor.fetchone()[0] == 0:
        for k, v in DEFAULT_CONFIG.items():
            cursor.execute("INSERT INTO configuracion (clave, valor) VALUES (?, ?)", (k, v))
            
    conn.commit()
    return conn

def get_config(db_path="data/historial_sara.sqlite3"):
    """Lee toda la configuración en SQLite y parsea sus tipos de datos."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT clave, valor FROM configuracion")
    rows = cursor.fetchall()
    conn.close()
    
    config = {}
    for clave, valor in rows:
        if valor.lower() in ["true", "false"]:
            config[clave] = valor.lower() == "true"
        elif valor.startswith("[") or valor.startswith("{"):
            try:
                config[clave] = json.loads(valor)
            except:
                config[clave] = valor
        elif valor.isdigit():
            config[clave] = int(valor)
        else:
            config[clave] = valor
    return config

def update_config(updates: dict, db_path="data/historial_sara.sqlite3"):
    """Actualiza una o varias llaves en la configuración y persiste en SQLite."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    for k, v in updates.items():
        if isinstance(v, bool):
            val_str = "true" if v else "false"
        elif isinstance(v, (list, dict)):
            val_str = json.dumps(v)
        else:
            val_str = str(v)
        cursor.execute("INSERT OR REPLACE INTO configuracion (clave, valor) VALUES (?, ?)", (k, val_str))
    conn.commit()
    conn.close()
