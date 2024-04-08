import asyncio

from aiogram import types
from django.conf import settings
from fastapi import APIRouter, BackgroundTasks
from starlette.requests import Request

from question_app.models import KnowledgeBase
from question_app.utils import Transformer

api_router = APIRouter()


@api_router.post(settings.WEBHOOK_PATH)
async def bot_webhook(update: dict, request: Request):
    telegram_update = types.Update(**update)
    dp = request.state.dp
    bot = request.state.bot
    await dp._process_update(bot=bot, update=telegram_update)


@api_router.get(settings.WEBHOOK_PATH)
async def bot_status(request: Request):
    bot = request.state.bot
    return await bot.me()


@api_router.get("/similar")
def get_n_similar(question: str = "", n: int = 5):
    transformer = Transformer.get()
    result = {
        "searchQuery": question,
        "topN": n,
        "similarityThreshold": transformer.similarity_threshold,
        "considerSimilar": transformer.consider_similar,
        "suggestions": [],
        "resultLen": 0,
    }
    if question:
        articles_similarity = transformer.find_n_similar(question, n)
        articles_with_similarity = []
        for article_name, similarity in articles_similarity:
            article = KnowledgeBase.objects.filter(question=article_name).first()
            if article:
                articles_with_similarity.append(
                    {
                        "question": article.question,
                        "answer": article.answer,
                        "similarity": similarity,
                    }
                )
        result["suggestions"].extend(articles_with_similarity)
        result["resultLen"] += len(articles_with_similarity)
    return result


@api_router.get("/bot")
async def get_bot_status(background_tasks: BackgroundTasks):
    tasks = [t for t in asyncio.all_tasks() if t.get_name() == "tg_bot"]
    task = None

    if not tasks:
        return (True, True)
    if tasks:
        task = tasks[0]
    return (task.done(), task.cancelled())
