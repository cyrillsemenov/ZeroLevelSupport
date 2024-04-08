"""
ASGI config for webapp project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from contextlib import asynccontextmanager

from django.apps import apps
from django.conf import settings
from django.core.wsgi import get_wsgi_application
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from starlette.middleware.cors import CORSMiddleware

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webapp.settings")
apps.populate(settings.INSTALLED_APPS)

# trunk-ignore(ruff/E402)
from question_app.endpoints import api_router

# trunk-ignore(ruff/E402)
from telegram_bot.bot_start import BotMiddleware, bot


@asynccontextmanager
async def lifespan(_: FastAPI):
    await bot.set_webhook(
        url=settings.WEBHOOK_URL,
        secret_token=settings.WEBHOOK_SECRET,
    )

    try:
        yield
    finally:
        await bot.delete_webhook(drop_pending_updates=settings.BOT_SKIP_UPDATES)


def get_application() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.PROJECT_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(
        BotMiddleware,
        api_token=settings.BOT_API_KEY,
        secret_token=settings.WEBHOOK_SECRET,
    )
    app.include_router(api_router, prefix="/api")
    app.mount("/django", WSGIMiddleware(get_wsgi_application()))
    return app


app = get_application()
