import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from django.conf import settings
from django.core.management.base import BaseCommand

from ...handlers import handle_user_message, report, support


class Command(BaseCommand):
    @staticmethod
    def setup_dispatcher() -> Dispatcher:
        dp = Dispatcher()
        dp.include_routers(handle_user_message.router)
        dp.include_routers(report.router)
        dp.include_routers(support.router)
        return dp

    def add_arguments(self, parser):
        parser.add_argument(
            "--bot-api-key",
            type=str,
            help="Telegram bot API key",
            default=os.getenv("BOT_API_KEY"),
        )
        parser.add_argument(
            "--parse-mode",
            type=str,
            help="Model name for embeddings",
            default=os.getenv("PARSE_MODE", ParseMode.HTML.value),
            choices=[mode.value for mode in ParseMode],
        )
        parser.add_argument(
            "--link-preview",
            type=str,
            help="Link preview size",
            choices=["large", "small", "disable"],
            default="large",
        )
        parser.add_argument(
            "--link-preview-above-text",
            action="store_true",
            help="Show link preview above text",
        )
        parser.add_argument(
            "--do-not-send-without-reply",
            action="store_false",
            help="Do not send without reply",
        )
        parser.add_argument(
            "--skip-updates",
            action="store_true",
            help="Skip pending updates",
        )

    def handle(self, *args, **options):

        async def start_polling() -> None:
            dp = self.setup_dispatcher()
            bot = Bot(settings.BOT_API_KEY, default=settings.BOT_PROPERTIES)
            if settings.BOT_SKIP_UPDATES:
                await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)

        asyncio.run(start_polling())
