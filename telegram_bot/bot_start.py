from logging import getLogger
from typing import Optional

from aiogram import Bot, Dispatcher
from django.conf import settings
from fastapi import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware, DispatchFunction
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from .handlers import handle_user_message, report, support

logger = getLogger(__name__)


def setup_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.include_routers(handle_user_message.router)
    dp.include_routers(report.router)
    dp.include_routers(support.router)
    return dp


dp = setup_dispatcher()
bot = Bot(settings.BOT_API_KEY, default=settings.BOT_PROPERTIES)


class BotMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        dispatch: Optional[DispatchFunction] = None,
        api_token: Optional[str] = None,
        secret_token: Optional[str] = None,
    ) -> None:
        super().__init__(app, dispatch)
        self.api_token = api_token
        self.secret_token = secret_token

    async def dispatch(self, request: Request, call_next) -> Response:
        token_good = request.url.path.split("/")[-1] == self.api_token
        secret_good = (
            request.headers.get("x-telegram-bot-api-secret-token") == self.secret_token
        )
        if request.url.path.startswith("/api/bot") and not (token_good and secret_good):
            raise HTTPException(
                status_code=403,
                detail="Access denied",
                headers={"X-Error": "Wrong telegram bot secret token"},
            )
        request.state.bot = bot
        request.state.dp = dp
        response = await call_next(request)
        return response
