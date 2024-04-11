from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class ArticleSchema(BaseModel):
    question: str
    answer: Optional[str] = None
    embedding: List[float] = []
    flags: List[str] = []

    def __repr__(self) -> str:
        return f"Article(question = '{self.question}', flags = [{self.flags}])"

    def __str__(self) -> str:
        return self.__repr__()


class SynonymSchema(BaseModel):
    question: str
    embedding: List[float] = []
    pointer: ArticleSchema

    def __repr__(self) -> str:
        return f"Synonym('{self.question}' = '{self.pointer.question}')"

    def __str__(self) -> str:
        return self.__repr__()