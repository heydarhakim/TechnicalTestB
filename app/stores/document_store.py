import os
from typing import List, Optional, Any
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

class DocumentStore:
    def __init__(self):
        self.using_qdrant = False
        self.client: Optional[QdrantClient] = None
        self.collection_name = "demo_collection"
        self.vector_size = 128
        
        # In-memory fallback
        self.docs_memory: List[str] = []
        
        # Internal counter to ensure unique IDs (fixing the issue in original code 
        # where IDs were based on len(docs_memory) which didn't increment in Qdrant mode)
        self._doc_counter = 0

        self._init_qdrant()

    def _init_qdrant(self):
        try:
            # Assumes local instance as per original code
            self.client = QdrantClient("http://localhost:6333")
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE)
            )
            self.using_qdrant = True
        except Exception as e:
            print("⚠️  Qdrant not available. Falling back to in-memory list.")
            self.using_qdrant = False

    def add(self, text: str, vector: List[float]) -> int:
        doc_id = self._doc_counter
        self._doc_counter += 1

        if self.using_qdrant:
            payload = {"text": text}
            self.client.upsert(
                collection_name=self.collection_name,
                points=[PointStruct(id=doc_id, vector=vector, payload=payload)]
            )
        else:
            self.docs_memory.append(text)
        
        return doc_id

    def search(self, query_text: str, query_vector: List[float], limit: int = 2) -> List[str]:
        results = []

        if self.using_qdrant:
            hits = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit
            )
            for hit in hits:
                results.append(hit.payload["text"])
        else:
            # Replicating original substring logic
            for doc in self.docs_memory:
                if query_text.lower() in doc.lower():
                    results.append(doc)
            # Fallback: Just grab first if nothing found but docs exist
            if not results and self.docs_memory:
                results = [self.docs_memory[0]]
        
        return results

    def get_status(self):
        return {
            "qdrant_ready": self.using_qdrant,
            "in_memory_docs_count": len(self.docs_memory)
        }