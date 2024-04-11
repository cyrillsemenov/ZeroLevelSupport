from __future__ import annotations

from functools import wraps
from typing import Any, Dict, List, Optional, Tuple, Type

import sniffio
from asgiref.sync import async_to_sync, sync_to_async
from django.db.models import Model

from question_app.solver.base import DatabaseAdapterBase
from question_app.solver.schemas import ArticleSchema, SynonymSchema

from ...base import lru_cache
from .models import KnowledgeBase, Synonym


def is_async() -> bool:
    try:
        return sniffio.current_async_library() is not None
    except sniffio.AsyncLibraryNotFoundError:
        return False


def async_aware(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if is_async():
            print(f"Async call {func.__name__}")
            return sync_to_async(func)(*args, **kwargs)
        else:
            print(f"Sync call {func.__name__}")
            return func(*args, **kwargs)

    return wrapper


def execute_in_context(func, *args, **kwargs):
    if is_async():
        return async_to_sync(func)(*args, **kwargs)
    else:
        return func(*args, **kwargs)


def get_objects_sync(model: Type[Model], **filters: Dict[str, Any]) -> Tuple[Model]:
    return model.objects.filter(
        **{k: v for k, v in filters.items() if v is not None}
    ).all()


async def get_objects_async(
    model: Type[Model], **filters: Dict[str, Any]
) -> Tuple[Model]:
    return await sync_to_async(get_objects_sync)(model, **filters)


class DjangoAdapter(DatabaseAdapterBase):
    @async_aware
    def update_vectors(self, update_all: bool = False):
        self.get_knowledge.cache_clear()
        self.get_synonyms.cache_clear()
        questions: List[Model] = [
            *self.get_knowledge(),
            *self.get_synonyms(),
        ]
        question_titles = [
            q.question for q in questions if update_all or q.embedding is None
        ]

        def save(vectors):
            for question, embedding in zip(questions, vectors):
                question.set_embedding(embedding)
                # if is_async():
                #     execute_in_context(question.aset_embedding, embedding)
                # else:
                #     execute_in_context(question.set_embedding, embedding)

        return question_titles, save

    @async_aware
    @lru_cache(maxsize=64)
    def get_knowledge(self, question: Optional[str] = None) -> Tuple[ArticleSchema]:
        filters = [
            ("question", question),
        ]
        objects = KnowledgeBase.objects.filter(
            **{k: v for k, v in filters if v is not None}
        ).all()
        return [
            ArticleSchema(
                question=o.question,
                answer=o.answer,
                embedding=o.get_embedding(),
                flags=[f.name for f in (o.flags.all() or [])],
            )
            for o in objects
        ]

    @async_aware
    @lru_cache(maxsize=64)
    def get_synonyms(self, question: Optional[str] = None) -> Tuple[SynonymSchema]:
        filters = [
            ("question", question),
        ]
        objects = Synonym.objects.filter(
            **{k: v for k, v in filters if v is not None}
        ).all()
        return [
            SynonymSchema(
                question=o.question,
                pointer=self.get_knowledge(question=o.pointer.question)[0],
                embedding=o.get_embedding(),
            )
            for o in objects
        ]
