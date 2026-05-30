import os
import sys
import json
import time

# Resolver importaciones relativas si se corre desde scripts/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ingestion.pdf_parser import DocumentParser
from src.brain.text_chunker import TextChunker
from src.brain.vector_db import VectorDBContext

def main():
    print("=== FASE 9: Ingesta Masiva Vectorial ===")
    
    RAW_DIR = "/home/analitica/SARA/data/01_raw_icesi"
    PROCESSED_DIR = "/home/analitica/SARA/data/02_processed"
    VECTOR_DB_DIR = "/home/analitica/SARA/data/04_vector_db"
    
    # Recopilar TODOS los documentos
    all_files = []
    for root, _, files in os.walk(RAW_DIR):
        for f in files:
            if f.endswith('.pdf') or f.endswith('.docx'):
                all_files.append(os.path.join(root, f))
                
    if not all_files:
        print("No se encontraron archivos en la carpeta raw.")
        return
        
    print(f"\n1. Procesando la totalidad del corpus: {len(all_files)} documentos.")
    
    parser = DocumentParser(raw_dir=RAW_DIR, processed_dir=PROCESSED_DIR)
    chunker = TextChunker(chunk_size=1200, chunk_overlap=150)
    
    # Inicializar Base Vectorial (esto cargará el modelo bge-m3 en GPU)
    vector_db = VectorDBContext(persist_directory=VECTOR_DB_DIR)
    
    start_time = time.time()
    for idx, file_path in enumerate(all_files, 1):
        print(f"\n--- [{idx}/{len(all_files)}] Procesando: {os.path.basename(file_path)} ---")
        
        # A. Ingesta y Limpieza
        parsed_docs = parser.process_batch([file_path])
        text = parsed_docs.get(file_path)
        if not text:
            print("    [!] Documento vacío o con error de lectura. Omitiendo.")
            continue
            
        print(f"    - Texto extraído: {len(text)} caracteres")
        
        # B. Chunking
        chunks = chunker.split_text(text)
        print(f"    - Fragmentado en {len(chunks)} chunks")
        
        # C. Indexación Vectorial
        vector_db.add_chunks(file_path, chunks)
        
    end_time = time.time()
    print(f"\n=== INGESTA MASIVA COMPLETADA ===")
    print(f"Tiempo total: {(end_time - start_time)/60:.2f} minutos.")

if __name__ == "__main__":
    main()
