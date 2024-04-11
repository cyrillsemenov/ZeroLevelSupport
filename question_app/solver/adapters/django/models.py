from typing import List

import numpy as np
from asgiref.sync import sync_to_async
from django.db.models import (
    CASCADE,
    BinaryField,
    CharField,
    ForeignKey,
    ManyToManyField,
    Model,
    TextField,
)


class Flag(Model):
    name = CharField(unique=True, max_length=255)
    comment = TextField(blank=True)

    def __str__(self):
        return self.name


class KnowledgeBase(Model):
    question = TextField(unique=True)
    answer = TextField(null=True, blank=True)
    flags = ManyToManyField(Flag, blank=True)
    embedding = BinaryField(null=True, blank=True)

    def get_flags(self) -> List[str]:
        return [f.name for f in self.flags.all()]

    async def a_get_flags(self) -> List[str]:
        return await sync_to_async(self.get_flags)()

    def set_flag(self, flag: str):
        group, _ = Flag.objects.get_or_create(name=flag)
        self.flags.add(group)
        self.save()

    async def a_set_flag(self, flag: str):
        await sync_to_async(self.set_flag)(flag)

    def set_embedding(self, embedding: List[float]) -> None:
        """Stores the embedding list as bytes in the database."""
        self.embedding = np.array(embedding, dtype=np.float32).tobytes()
        self.save()

    async def aset_embedding(self, embedding: List[float]) -> None:
        await sync_to_async(self.set_embedding)(embedding)

    def get_embedding(self) -> List[float]:
        """Retrieves and converts the embedding bytes back to a list of floats."""
        if self.embedding:
            return np.frombuffer(self.embedding, dtype=np.float32).tolist()
        return []

    def has_embedding(self):
        return bool(self.embedding)

    def __str__(self):
        return self.question


class Synonym(Model):
    question = TextField(unique=True)
    pointer = ForeignKey(KnowledgeBase, related_name="synonyms", on_delete=CASCADE)
    embedding = BinaryField(null=True, blank=True)

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
        return f"{self.question} == {self.pointer.question}"
