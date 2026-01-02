from langgraph.graph import StateGraph, END
from .embedding import EmbeddingService
from ..stores.document_store import DocumentStore

class RagWorkflow:
    def __init__(self, store: DocumentStore):
        self.store = store
        self.chain = self._build_graph()

    def _retrieve(self, state):
        query = state["question"]
        
        # Embed query using the service
        emb = EmbeddingService.embed(query)
        
        # Search using the store
        results = self.store.search(query_text=query, query_vector=emb, limit=2)
        
        state["context"] = results
        return state

    def _answer(self, state):
        ctx = state["context"]
        if ctx:
            answer = f"I found this: '{ctx[0][:100]}...'"
        else:
            answer = "Sorry, I don't know."
        state["answer"] = answer
        return state

    def _build_graph(self):
        workflow = StateGraph(dict)
        workflow.add_node("retrieve", self._retrieve)
        workflow.add_node("answer", self._answer)
        
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "answer")
        workflow.add_edge("answer", END)
        
        return workflow.compile()

    def run(self, input_data: dict):
        return self.chain.invoke(input_data)