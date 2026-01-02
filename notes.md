Main Design Decisions I encapsulated the data access logic into DocumentStore. The original code mixed database connection strings, in-memory lists, and conditional if USING_QDRANT checks directly inside API logic and helper functions. By moving this to stores/document_store.py, the rest of the app (specifically the RAG workflow) no longer needs to know which backend is active; it simply calls .search() or .add().

Trade-off Considered I had to make a decision regarding ID generation. In the original main.py, doc_id = len(docs_memory) was used. When Qdrant was active, docs_memory remained empty, meaning every new document was assigned ID 0 (overwriting the previous one). This was likely a bug in the original code.

    Decision: I introduced self._doc_counter in the DocumentStore to ensure unique IDs are generated regardless of the storage backend. This slightly changes internal behavior (it fixes a bug) but preserves the external API contract of returning an integer ID.

Maintainability Improvements

    Separation of Concerns: Embedding logic is now separated from retrieval logic. If you decide to swap fake_embed for OpenAI or HuggingFace later, you only change services/embedding.py.

    Testability: You can now instantiate DocumentStore in a unit test to verify the fallback logic without needing to run the full FastAPI server.

    Readability: The RagWorkflow class clearly defines the graph structure in one place, rather than having nodes defined as loose functions in the global scope.