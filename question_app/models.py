from typing import List
from django.db import models
import numpy as np

class KnowledgeBase(models.Model):
    question = models.TextField(unique=True)
    answer = models.TextField()
    embedding = models.BinaryField(null=True, blank=True)

    def set_embedding(self, embedding: List[float]) -> None:
        """Stores the embedding list as bytes in the database."""
        self.embedding = np.array(embedding, dtype=np.float32).tobytes()

    def get_embedding(self) -> List[float]:
        """Retrieves and converts the embedding bytes back to a list of floats."""
        if self.embedding:
            return np.frombuffer(self.embedding, dtype=np.float32).tolist()
        return []
    
    def has_embedding(self):
        return bool(self.embedding)

    def __str__(self):
        return self.question