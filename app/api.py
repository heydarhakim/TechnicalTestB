import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .services.embedding import EmbeddingService
from .services.rag import RagWorkflow
from .stores.document_store import DocumentStore

router = APIRouter()

store = DocumentStore()
rag_service = RagWorkflow(store)

# --- Pydantic Models ---
class QuestionRequest(BaseModel):
    question: str

class DocumentRequest(BaseModel):
    text: str

# Endpoints 

@router.post("/ask")
def ask_question(req: QuestionRequest):
    start = time.time()
    try:
        result = rag_service.run({"question": req.question})
        return {
            "question": req.question,
            "answer": result["answer"],
            "context_used": result.get("context", []),
            "latency_sec": round(time.time() - start, 3)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add")
def add_document(req: DocumentRequest):
    try:
        emb = EmbeddingService.embed(req.text)
        doc_id = store.add(req.text, emb)
        return {"id": doc_id, "status": "added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
def status():
    # Merge store status with graph status
    s = store.get_status()
    s["graph_ready"] = rag_service.chain is not None
    return s