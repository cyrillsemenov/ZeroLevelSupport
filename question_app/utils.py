from __future__ import annotations

import logging
import os
import string
from typing import Callable, Dict, List, Optional

from asgiref.sync import sync_to_async

# import numpy as np
from openai import OpenAI
from openai.types.embedding import Embedding
from sklearn.metrics.pairwise import cosine_similarity

from question_app.models import KnowledgeBase

logger = logging.getLogger(__name__)

REMOVE_PUNCTUATION = str.maketrans("", "", string.punctuation + "\n\r")


class Transformer:
    _transformer: Transformer
    _transformer_ready = False
    _base: Dict[str, List[float]] = {}

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
            q.question: q.get_embedding() for q in KnowledgeBase.objects.all()
        }
        self.prepare_str = prepare_str

    def generate_embeddings(self, texts: List[str], **kwargs) -> List[Embedding]:
        if not texts:
            return []
        texts = [self.prepare_str(t) for t in texts]
        response = self.client.embeddings.create(
            input=texts, model=self.model, **kwargs
        )
        return [e.embedding for e in response.data]

    def update_base(self, update_all: bool = False) -> None:
        questions = KnowledgeBase.objects.all()
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

        self._base.update(
            {q.question: q.get_embedding() for q in KnowledgeBase.objects.all()}
        )

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
        similarities = cosine_similarity(q, list(self._base.values()))

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

    @classmethod
    def get(
        cls, api_key: Optional[str] = None, model: str = "text-embedding-3-large"
    ) -> Transformer:
        if not cls._transformer_ready:
            api_key = os.getenv("OPENAI_API_KEY", api_key)
            if api_key:
                cls._transformer = Transformer(api_key, model)
                cls._transformer_ready = True
            else:
                raise RuntimeError("Provide OpenAI API key and model name")
        return cls._transformer

    @classmethod
    async def a_get(
        cls, api_key: Optional[str] = None, model: str = "text-embedding-3-large"
    ) -> Transformer:
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
