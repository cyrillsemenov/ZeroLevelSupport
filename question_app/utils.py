from __future__ import annotations

import os
from typing import List, Optional
from openai import OpenAI
from openai.types.embedding import Embedding

class Transformer:
    _transformer: Transformer
    _transformer_ready = False

    def __init__(self, api_key: str, model: str) -> None:
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def generate_embeggings(self, texts: List[str], **kwargs) -> List[Embedding]:
        response = self.client.embeddings.create(
            input=texts,
            model=self.model,
            **kwargs
        )
        return [e.embedding for e in response.data]

    @classmethod
    def get(cls, api_key: Optional[str] = None, model: str = 'text-embedding-ada-002') -> Transformer:
        if not cls._transformer_ready:
            api_key = os.getenv("OPENAI_API_KEY", api_key)
            if api_key:
                cls._transformer = Transformer(api_key, model)
                cls._transformer_ready = True
            else:
                raise RuntimeError("Provide OpenAI API key and model name")
        return cls._transformer

