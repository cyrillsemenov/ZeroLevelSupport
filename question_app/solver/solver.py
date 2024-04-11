from __future__ import annotations

import logging
import os
from typing import List, Optional

import numpy as np
from asgiref.sync import sync_to_async

# from openai.types.embedding import Embedding
from pydantic import BaseModel, Field
from sklearn.metrics.pairwise import cosine_similarity

from .adapters.django import DjangoAdapter
from .base import DatabaseAdapterBase, EncoderBase, SingletonMeta
from .encoders.openai import OpenAIEncoder
from .schemas import SynonymSchema

logger = logging.getLogger(__name__)


class SolverSettings(BaseModel):
    similarity_threshold: float = Field(
        ..., default_factory=lambda: os.getenv("SIMILARITY_THRESHOLD", 0.31)
    )
    consider_similar: float = Field(
        ..., default_factory=lambda: os.getenv("CONSIDER_SIMILAR", 0.81)
    )


class Solver(metaclass=SingletonMeta):
    database: DatabaseAdapterBase = DjangoAdapter()
    encoder: EncoderBase = OpenAIEncoder()
    default_settings: SolverSettings = SolverSettings()

    def __init__(self) -> None:
        self.similarity_threshold = self.default_settings.similarity_threshold
        self.consider_similar = self.default_settings.consider_similar

    def find_synonym(self, vector: List[List[float]]) -> Optional[List[List[float]]]:
        synonym_base = self.database.get_synonyms()
        synonyms = cosine_similarity(vector, [s.embedding for s in synonym_base])
        top_indices = np.argsort(synonyms[0])[::-1][:1]
        similar_questions: List[SynonymSchema] = [
            synonym_base[i]
            for i in top_indices
            if synonyms[0][i] >= self.consider_similar
        ]
        if similar_questions:
            return [similar_questions[0].pointer.embedding]
        return None

    def find_n_similar(
        self,
        text: str,
        top_k: int = 5,
        similarity_threshold: Optional[float] = None,
        consider_similar: Optional[float] = None,
    ) -> List[str]:
        if similarity_threshold is None:
            similarity_threshold = self.similarity_threshold
        if consider_similar is None:
            consider_similar = self.consider_similar

        # self.update_base()
        q = self.encoder.generate_embeddings(text)
        synonym = self.find_synonym(q)
        if synonym:
            q = synonym

        kb = self.database.get_knowledge()
        similarities = cosine_similarity(q, [q.embedding for q in kb])

        # Filter out the indices and similarity scores that meet the similarity_threshold
        filtered_indices_and_scores = [
            (index, score)
            for index, score in enumerate(similarities.flatten())
            if score > similarity_threshold
        ]

        # Get the top K indices and scores, considering the similarity_threshold
        top_indices_and_scores = sorted(
            filtered_indices_and_scores, key=lambda x: x[1], reverse=True
        )[:top_k]

        similar_questions = [
            ([q.question for q in kb][index], score)
            for index, score in top_indices_and_scores
        ]

        return similar_questions

    def get_flags(self, key: str) -> List[str]:
        articles = self.database.get_knowledge(question=key)
        if articles:
            return articles[0].flags

    async def a_get_flags(self, key: str) -> List[str]:
        return await sync_to_async(self.get_flags)(key)

    async def a_find_n_similar(
        self,
        text: str,
        top_k: int = 5,
        similarity_threshold: Optional[float] = None,
        consider_similar: Optional[float] = None,
    ) -> List[str]:
        return await sync_to_async(self.find_n_similar)(
            text,
            top_k,
            similarity_threshold,
            consider_similar,
        )

    def __enter__(self) -> Solver:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return


class AsyncSolver:
    def __init__(self, solver: Solver) -> None:
        self.solver = solver

    async def find_n_similar(
        self,
        text: str,
        top_k: int = 5,
        similarity_threshold: Optional[float] = None,
        consider_similar: Optional[float] = None,
    ) -> List[str]:
        return await sync_to_async(self.solver.find_n_similar)(
            text,
            top_k,
            similarity_threshold,
            consider_similar,
        )

    async def __aenter__(self) -> Solver:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return
