from typing import List

from pydantic import BaseModel

from question_app.solver import Solver


class Article(BaseModel):
    question: str
    similarity: float
    answer: str = ""
    flags: List[str]


class SearchResult(BaseModel):
    search_query: str
    top_n: int
    similarity_threshold: float
    consider_similar: float
    suggestions: List[Article] = []
    result_len: int = 0

    @classmethod
    def default(cls, question: str, top: int, solver: Solver) -> "SearchResult":
        return cls(
            search_query=question,
            top_n=top,
            similarity_threshold=solver.similarity_threshold,
            consider_similar=solver.consider_similar,
        )
