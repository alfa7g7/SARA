import os
import time
import random
import re
import unicodedata
import fitz  # PyMuPDF
from docx import Document

class DocumentParser:
    def __init__(self, raw_dir: str, processed_dir: str):
        self.raw_dir = raw_dir
        self.processed_dir = processed_dir

    def clean_spanish_text(self, text: str) -> str:
        if not text:
            return ""
        
        # Normalización Unicode: asegura que tildes y ñ usen un solo punto de código
        text = unicodedata.normalize('NFKC', text)
        
        # Normalización exhaustiva de espacios (elimina saltos de línea innecesarios y múltiples espacios)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Opcional: remover caracteres extraños no imprimibles
        text = re.sub(r'[^\x00-\x7F\xA0-\xFF\u0100-\u017F\u00D1\u00F1\u00E1\u00E9\u00ED\u00F3\u00FA\u00C1\u00C9\u00CD\u00D3\u00DA]', '', text)
        
        return text

    def parse_pdf(self, file_path: str) -> str:
        text = ""
        try:
            with fitz.open(file_path) as doc:
                for page in doc:
                    text += page.get_text()
        except Exception as e:
            print(f"Error parsing PDF {file_path}: {e}")
        return self.clean_spanish_text(text)

    def parse_docx(self, file_path: str) -> str:
        text = ""
        try:
            doc = Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            print(f"Error parsing DOCX {file_path}: {e}")
        return self.clean_spanish_text(text)

    def process_batch(self, batch_files: list) -> dict:
        """
        Procesa archivos por lotes (batches) para no saturar la RAM.
        Devuelve un diccionario {file_path: text_content}
        """
        results = {}
        for file_path in batch_files:
            if file_path.lower().endswith('.pdf'):
                results[file_path] = self.parse_pdf(file_path)
            elif file_path.lower().endswith('.docx'):
                results[file_path] = self.parse_docx(file_path)
        return results

if __name__ == "__main__":
    import glob
    
    RAW_DIR = "/home/analitica/SARA/data/01_raw_icesi"
    
    # Listar archivos disponibles
    pdf_files = glob.glob(os.path.join(RAW_DIR, "*.pdf"))
    docx_files = glob.glob(os.path.join(RAW_DIR, "*.docx"))
    
    # Seleccionar lote aleatorio de hasta 10 PDFs y 10 Word docs (como dicta la prueba piloto)
    num_pdfs = min(10, len(pdf_files))
    num_docxs = min(10, len(docx_files))
    
    random_pdfs = random.sample(pdf_files, num_pdfs)
    random_docxs = random.sample(docx_files, num_docxs)
    pilot_batch = random_pdfs + random_docxs
    
    print(f"=== PRUEBA PILOTO (Benchmark Inicial) ===")
    print(f"Iniciando ingesta de lote: {len(random_pdfs)} PDFs y {len(random_docxs)} DOCXs...")
    
    parser = DocumentParser(raw_dir=RAW_DIR, processed_dir="/home/analitica/SARA/data/03_structured")
    
    # Medir tiempo de ejecución
    start_time = time.time()
    results = parser.process_batch(pilot_batch)
    end_time = time.time()
    
    print(f"\nTiempo total de ejecución del lote: {end_time - start_time:.2f} segundos.")
    print(f"Archivos procesados exitosamente: {len([r for r in results.values() if r])}/{len(pilot_batch)}")
    
    # Mostrar vista previa
    if results:
        # Extraer el primero que no esté vacío
        sample_file = next((f for f, text in results.items() if text), None)
        if sample_file:
            sample_text = results[sample_file]
            print(f"\n--- Vista previa de extracción: {os.path.basename(sample_file)} ---")
            print(sample_text[:500] + "..." if len(sample_text) > 500 else sample_text)
            print("-" * 60)
