from __future__ import annotations

import logging
import os
import string
from typing import Callable, Dict, List, Optional

import numpy as np
from asgiref.sync import sync_to_async
from django.db import models
from openai import OpenAI
from openai.types.embedding import Embedding
from sklearn.metrics.pairwise import cosine_similarity

from question_app.models import KnowledgeBase, Synonym

logger = logging.getLogger(__name__)

REMOVE_PUNCTUATION = str.maketrans("", "", string.punctuation + "\n\r")


class Solver:
    _solver: Solver
    _solver_ready = False
    _base: Dict[str, List[float]] = {}
    _synonyms: Dict[str, List[float]] = {}

    def __init__(
        self,
        api_key: str,
        model: str,
        similarity_threshold: float = 0.31,
        consider_similar: float = 0.81,
        prepare_str: Callable[[str], str] = lambda x: x.strip()
        .translate(REMOVE_PUNCTUATION)
        .casefold(),
    ) -> None:
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.similarity_threshold = similarity_threshold
        self.consider_similar = consider_similar
        self._base = {
            q.question: (q.get_embedding(), [f.name for f in (q.flags.all() or [])])
            for q in KnowledgeBase.objects.all()
        }
        self._synonyms = {q.question: q.get_embedding() for q in Synonym.objects.all()}
        self.prepare_str = prepare_str

    def generate_embeddings(self, texts: List[str], **kwargs) -> List[Embedding]:
        if not texts:
            return []
        texts = [self.prepare_str(t) for t in texts]
        response = self.client.embeddings.create(
            input=texts, model=self.model, **kwargs
        )
        return [e.embedding for e in response.data]

    def update_vectors(
        self,
        table: models.Model,
        # cache: Dict[str, List[float]],
        update_all: bool = False,
    ) -> List[models.Model]:
        questions = table.objects.all()
        question_titles = [
            q.question for q in questions if update_all or q.embedding is None
        ]
        if not question_titles:
            logger.debug("All embeddings are up to date...")
            return

        vectors = self.generate_embeddings(question_titles)
        if not vectors:
            return

        for question, embedding in zip(questions, vectors):
            question.set_embedding(embedding)
            question.save()

        return table.objects.all()
        # cache.update({q.question: q.get_embedding() for q in table.objects.all()})

    def update_base(self, update_all: bool = False) -> None:
        kb = self.update_vectors(KnowledgeBase, update_all)
        if kb:
            self._base.update(
                {
                    q.question: (
                        q.get_embedding(),
                        [f.name for f in (q.flags.all() or [])],
                    )
                    for q in kb
                }
            )
        s = self.update_vectors(Synonym)
        if s:
            self._synonyms.update({q.question: q.get_embedding() for q in s})

    def find_synonym(self, vector: List[List[float]]) -> Optional[List[List[float]]]:
        synonyms = cosine_similarity(vector, list(self._synonyms.values()))
        top_indices = np.argsort(synonyms[0])[::-1][:1]
        similar_questions = [
            list(self._synonyms.keys())[i]
            for i in top_indices
            if synonyms[0][i] >= self.consider_similar
        ]
        if similar_questions:
            synonym = Synonym.objects.get(question=similar_questions[0]).pointer
            return [synonym.get_embedding()]
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

        self.update_base()
        q = self.generate_embeddings([text])
        synonym = self.find_synonym(q)
        if synonym:
            q = synonym

        similarities = cosine_similarity(q, [q for q, _ in self._base.values()])

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
            (list(self._base.keys())[index], score)
            for index, score in top_indices_and_scores
        ]

        return similar_questions

    def get_flags(self, key: str) -> List[str]:
        _, flags = self._base.get(key, (None, []))
        return flags

    @classmethod
    def get(
        cls, api_key: Optional[str] = None, model: str = "text-embedding-3-large"
    ) -> Solver:
        if not cls._solver_ready:
            api_key = os.getenv("OPENAI_API_KEY", api_key)
            if api_key:
                cls._solver = Solver(api_key, model)
                cls._solver_ready = True
            else:
                raise RuntimeError("Provide OpenAI API key and model name")
        return cls._solver

    @classmethod
    async def a_get(
        cls, api_key: Optional[str] = None, model: str = "text-embedding-3-large"
    ) -> Solver:
        return await sync_to_async(cls.get)(api_key, model)

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
