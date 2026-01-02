import random
from typing import List

class EmbeddingService:
    @staticmethod
    def embed(text: str) -> List[float]:
        """
        Pretend this is a real embedding model.
        Seed based on input so it's 'deterministic'.
        """
        random.seed(abs(hash(text)) % 10000)
        return [random.random() for _ in range(128)]