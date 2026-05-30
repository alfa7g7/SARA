import os
import chromadb
from sentence_transformers import SentenceTransformer
import torch

class VectorDBContext:
    def __init__(self, persist_directory: str, collection_name: str = "sara_documents"):
        """
        Inicializa la conexión con ChromaDB y carga el modelo de Sentence Transformers
        usando CUDA si está disponible.
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Cliente persistente de ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=self.persist_directory)
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        # Verificar y usar explícitamente CUDA
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"[VectorDB] Cargando modelo en: {self.device}")
        
        # Cargar el modelo (optimizando para RAG multilingüe / español).
        # BAAI/bge-m3 es el SOTA para RAG multilingüe y alta densidad.
        self.model_name = "BAAI/bge-m3"
        self.model = SentenceTransformer(self.model_name, device=self.device)

    def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Genera embeddings para una lista de textos.
        """
        embeddings = self.model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()

    def add_chunks(self, file_path: str, chunks: list[str]):
        """
        Agrega los chunks de texto a la base de datos vectorial de ChromaDB.
        """
        if not chunks:
            return

        embeddings = self.get_embeddings(chunks)
        
        ids = [f"{os.path.basename(file_path)}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"source": file_path, "chunk_index": i} for i in range(len(chunks))]

        self.collection.add(
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
        print(f"[VectorDB] Se indexaron {len(chunks)} chunks del doc {os.path.basename(file_path)}.")
        
        # Limpieza de memoria
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    def search(self, query: str, top_k: int = 3, where: dict = None):
        """
        Busca los chunks más relevantes para una query filtrando por metadatos opcionalmente.
        """
        query_embedding = self.model.encode([query], show_progress_bar=False).tolist()
        
        args = {
            "query_embeddings": query_embedding,
            "n_results": top_k
        }
        if where:
            args["where"] = where
            
        results = self.collection.query(**args)
        return results
