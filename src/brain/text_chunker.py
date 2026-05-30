from langchain_text_splitters import RecursiveCharacterTextSplitter

class TextChunker:
    def __init__(self, chunk_size=1200, chunk_overlap=150):
        """
        Inicializa el chunker usando RecursiveCharacterTextSplitter.
        Tamaño de chunk adaptado (1200 y overlap 150) para mayor densidad de contexto.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )

    def split_text(self, text: str) -> list[str]:
        """
        Toma un texto completo y lo divide en chunks (fragmentos).
        """
        if not text:
            return []
        
        chunks = self.text_splitter.split_text(text)
        return chunks

    def process_batch(self, documents: dict) -> dict:
        """
        Recibe un diccionario con {file_path: text_content}
        y devuelve {file_path: [chunks]}
        """
        results = {}
        for file_path, text in documents.items():
            results[file_path] = self.split_text(text)
        return results
