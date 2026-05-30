import json
import sqlite3
import pandas as pd
import os
from sklearn.metrics import mean_absolute_error, precision_score, recall_score, f1_score

def main():
    # Definición de rutas
    json_path = os.path.join("data", "04_outputs", "golden_truth.json")
    db_path = os.path.join("data", "historial_sara.sqlite3")
    csv_out_path = os.path.join("data", "04_outputs", "comparativo_resultados.csv")
    
    # Verificar si el archivo Golden Truth existe
    if not os.path.exists(json_path):
        print(f"[ERROR] No se encontró el archivo Golden Truth en: {json_path}")
        return

    # 1. Leer Golden Truth
    with open(json_path, 'r', encoding='utf-8') as f:
        golden_data = json.load(f)
    
    # Normalizar datos para asegurar iteración estructurada
    if isinstance(golden_data, dict):
        items = []
        for k, v in golden_data.items():
            if isinstance(v, dict):
                v["id_proceso"] = v.get("id_proceso", k)
                items.append(v)
        golden_data = items

    # 2. Conectar a SQLite
    if not os.path.exists(db_path):
        print(f"[ERROR] La base de datos no existe aún en: {db_path}")
        return
        
    conn = sqlite3.connect(db_path)
    
    resultados = []
    y_true_reg = []
    y_pred_reg = []
    y_true_cls = []
    y_pred_cls = []
    
    print("\n" + "="*50)
    print("🚀 TÚNEL DE VIENTO: Evaluación Comparativa de SARA")
    print("="*50)
    
    for item in golden_data:
        id_proceso = item.get("id_proceso")
        v_humana = item.get("viabilidad_real_humana")
        
        if id_proceso is None or v_humana is None:
            continue
            
        # 3. Cruce de Datos en BD
        query = "SELECT viabilidad FROM evaluaciones WHERE id_proceso = ?"
        df_db = pd.read_sql_query(query, conn, params=(id_proceso,))
        
        if df_db.empty:
            print(f"[!] Pendiente: SARA aún no ha evaluado el contrato '{id_proceso}'")
            resultados.append({
                "id_proceso": id_proceso,
                "viabilidad_humana": v_humana,
                "viabilidad_sara": None,
                "estado": "No evaluado"
            })
            continue
            
        v_sara = df_db.iloc[0]['viabilidad']
        
        resultados.append({
            "id_proceso": id_proceso,
            "viabilidad_humana": v_humana,
            "viabilidad_sara": v_sara,
            "estado": "Evaluado"
        })
        
        # Almacenar para métricas
        y_true_reg.append(float(v_humana))
        y_pred_reg.append(float(v_sara))
        
        # Umbral "Aprobado" >= 70%
        y_true_cls.append(1 if float(v_humana) >= 70 else 0)
        y_pred_cls.append(1 if float(v_sara) >= 70 else 0)
        
    conn.close()
    
    # 4. Guardar resultados crudos en CSV
    os.makedirs(os.path.dirname(csv_out_path), exist_ok=True)
    df_res = pd.DataFrame(resultados)
    df_res.to_csv(csv_out_path, index=False, encoding='utf-8')
    
    # 5. Cálculo y Reporte de Métricas Finales
    print("\n" + "-"*50)
    print(f"📊 REPORTE DE MÉTRICAS (MUESTRA N={len(y_true_reg)})")
    print("-"*50)
    
    if len(y_true_reg) > 0:
        mae = mean_absolute_error(y_true_reg, y_pred_reg)
        precision = precision_score(y_true_cls, y_pred_cls, zero_division=0)
        recall = recall_score(y_true_cls, y_pred_cls, zero_division=0)
        f1 = f1_score(y_true_cls, y_pred_cls, zero_division=0)
        
        print(f"🔹 Error Absoluto Medio (MAE): {mae:.2f}% de desvío promedio")
        print(f"🔹 Precisión (Threshold >= 70%): {precision:.2%}")
        print(f"🔹 Recall (Threshold >= 70%):    {recall:.2%}")
        print(f"🔹 F1-Score (Threshold >= 70%):  {f1:.2%}")
        print("\n✅ Matriz comparativa guardada exitosamente en:")
        print(f"   📂 {csv_out_path}")
    else:
        print("\n⚠️ No hay contratos cruzados para calcular métricas de rendimiento.")
        
    print("="*50 + "\n")
        
if __name__ == "__main__":
    main()
