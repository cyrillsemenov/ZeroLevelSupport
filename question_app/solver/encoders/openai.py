from __future__ import annotations

import os
from typing import Any, Optional, Tuple, Union

from openai import OpenAI
from pydantic import Field

from question_app.solver.base import EncoderBase

from ..base import lru_cache


class OpenAIEncoder(EncoderBase):
    __hash__ = object.__hash__
    api_key: str = Field(..., default_factory=lambda: os.environ["OPENAI_API_KEY"])
    model: str = Field(
        ...,
        default_factory=lambda: os.getenv("EMBEDDING_MODEL", "text-embedding-3-large"),
    )
    client: Optional[OpenAI] = None

    def model_post_init(self, __context: Any) -> None:
        if not self.client:
            self.client = OpenAI(api_key=self.api_key)
        return super().model_post_init(__context)

    @lru_cache(maxsize=64)
    def generate_embeddings(
        self, texts: Union[str, Tuple[str]], **kwargs
    ) -> Tuple[float]:
        if not isinstance(texts, (list, tuple, set)):
            texts = [texts]
        if not texts:
            return tuple([])
        texts = tuple([self._prepare_str(t) for t in texts])
        response = self.client.embeddings.create(
            input=texts, model=self.model, **kwargs
        )
        return tuple([e.embedding for e in response.data])
