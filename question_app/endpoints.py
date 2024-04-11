from typing import Annotated

from aiogram import types
from django.conf import settings
from fastapi import APIRouter, Depends, Header, HTTPException
from starlette.requests import Request

from question_app.schemas import Article, SearchResult
from question_app.solver import Solver
from question_app.solver.adapters.django import KnowledgeBase

api_router = APIRouter()


async def verify_secret(x_telegram_bot_api_secret_token: Annotated[str, Header()]):
    if x_telegram_bot_api_secret_token != settings.WEBHOOK_SECRET:
        raise HTTPException(status_code=404)


@api_router.post(
    settings.WEBHOOK_PATH,
    # response_model=types.Update | types.ErrorEvent,
    dependencies=[
        Depends(verify_secret),
    ],
)
async def bot_webhook(bot_token: str, update: dict, request: Request):
    if bot_token != settings.BOT_API_KEY:
        raise HTTPException(status_code=404)
    telegram_update = types.Update(**update)
    dp = request.state.dp
    bot = request.state.bot
    await dp._process_update(bot=bot, update=telegram_update)


@api_router.get(
    settings.WEBHOOK_PATH,
    response_model=types.User,
)
async def bot_status(bot_token: str, request: Request):
    if bot_token != settings.BOT_API_KEY:
        raise HTTPException(status_code=404)
    bot = request.state.bot
    return await bot.me()


@api_router.get("/similar", response_model=SearchResult)
def get_n_similar(question: str = "", n: int = 5):
    solver = Solver()
    result = SearchResult.default(question, n, solver)
    if question:
        articles_similarity = solver.find_n_similar(question, n)
        articles_with_similarity = []
        for article_name, similarity in articles_similarity:
            article = KnowledgeBase.objects.filter(question=article_name).first()
            if article:
                articles_with_similarity.append(
                    Article(
                        question=article.question,
                        similarity=similarity,
                        answer=article.answer,
                        flags=solver.get_flags(article.question),
                    )
                )
        result.suggestions.extend(articles_with_similarity)
        result.result_len += len(articles_with_similarity)
    return result
