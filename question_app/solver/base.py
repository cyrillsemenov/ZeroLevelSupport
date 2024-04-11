from __future__ import annotations

import functools
import string
from threading import Lock
from types import MethodType
from typing import Any, Callable, List, Optional, Tuple, Union

from pydantic import BaseModel

from question_app.solver.schemas import ArticleSchema, SynonymSchema

REMOVE_PUNCTUATION = str.maketrans("", "", string.punctuation + "\n\r")


def prepare_string(s: str) -> str:
    return s.strip().translate(REMOVE_PUNCTUATION).casefold()


def lru_cache(maxsize=128, typed=False):
    def decorator(func):
        @functools.wraps(func)
        def new_func(*args, **kwargs):
            new_args = tuple(
                tuple(arg) if isinstance(arg, list) else arg for arg in args
            )
            new_kwargs = {
                k: tuple(v) if isinstance(v, list) else v for k, v in kwargs.items()
            }
            return cached_func(*new_args, **new_kwargs)

        cached_func = functools.lru_cache(maxsize=maxsize, typed=typed)(func)
        new_func.cache = cached_func
        new_func.cache_clear = cached_func.cache_clear
        new_func.cache_info = cached_func.cache_info
        return new_func

    return decorator


class SingletonMeta(type):
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class EncoderBase(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    _prepare_str: Callable[[str], str] = staticmethod(prepare_string)

    def model_post_init(self, __context: Any) -> None:
        if isinstance(self._prepare_str, MethodType):
            raise TypeError(
                f"Ensure that {self._prepare_str.__name__} is wrapped with staticmethod() upon assignment in {self.__class__.__name__}."
            )
        return super().model_post_init(__context)

    def generate_embeddings(
        self, texts: Union[str, Tuple[str]], **kwargs
    ) -> Tuple[float]: ...


class DatabaseAdapterBase(metaclass=SingletonMeta):
    def update_vectors(self, update_all: bool = False): ...

    def get_knowledge(self, question: Optional[str] = None) -> List[ArticleSchema]: ...

    def get_synonyms(self, question: Optional[str] = None) -> List[SynonymSchema]: ...
