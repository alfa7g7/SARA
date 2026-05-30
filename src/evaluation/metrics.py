class ExtractionMetrics:
    @staticmethod
    def calculate_metrics(golden_truth: dict, prediction: dict) -> dict:
        """
        Calcula TP, FP, FN, Precision, Recall y F1-Score para una extracción.
        Compara las claves compartidas entre golden_truth y prediction.
        """
        tp = 0
        fp = 0
        fn = 0
        
        # Consideraremos todos los campos que existan en el golden_truth
        keys_to_evaluate = set(golden_truth.keys())
        
        for key in keys_to_evaluate:
            golden_val = golden_truth.get(key)
            pred_val = prediction.get(key)
            
            # Normalizar valores para comparación (evitar None vs "null" string, espacios, etc)
            g_str = str(golden_val).strip().lower() if golden_val is not None else ""
            p_str = str(pred_val).strip().lower() if pred_val is not None else ""
            
            # Si el humano dice que hay un valor real (no vacío/null)
            if g_str and g_str != "null" and g_str != "none":
                if p_str and p_str != "null" and p_str != "none":
                    if g_str in p_str or p_str in g_str:
                        tp += 1
                    else:
                        fp += 1
                        fn += 1 # We missed the true golden value AND we hallucinated a new one.
                else:
                    fn += 1 # We omitted the true value, model returned null.
            else:
                # El humano dice que el valor es nulo (no existe en el texto)
                if p_str and p_str != "null" and p_str != "none":
                    # El modelo inventó un valor que no existe (Alucinación)
                    fp += 1
                else:
                    # True Negative (TN): Ambos concuerdan en que es nulo. No suma para F1-Score típico de extracción,
                    # pero indica un comportamiento correcto.
                    pass

        # Precauciones de división por cero
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        
        f1_score = 0.0
        if precision > 0 or recall > 0:
            f1_score = 2 * (precision * recall) / (precision + recall)
            
        return {
            "True Positives (TP)": tp,
            "False Positives (FP)": fp,
            "False Negatives (FN)": fn,
            "Precision": round(precision, 4),
            "Recall": round(recall, 4),
            "F1-Score": round(f1_score, 4)
        }
