import os
import asyncio
import functools
from typing import Tuple

from django.core.management.base import BaseCommand
from django.conf import settings

import aiogram

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

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
        parser.add_argument('--bot-api-key', type=str, help='Telegram bot API key', default=os.getenv('BOT_API_KEY'))
        parser.add_argument('--parse-mode', type=str, help='Model name for embeddings', default=os.getenv('PARSE_MODE', ParseMode.HTML.value), choices=[mode.value for mode in ParseMode])
        parser.add_argument(
            "--link-preview",
            type=str,
            help="Link preview size",
            choices=["large", "small", "disable"],
            default="large"
        )
        parser.add_argument(
            "--link-preview-above-text",
            action='store_true',
            help="Show link preview above text",
        )
        parser.add_argument(
            "--do-not-send-without-reply",
            action='store_false',
            help="Do not send without reply",
        )
        parser.add_argument(
            "--skip-updates",
            action='store_true',
            help="Skip pending updates",
        )

    def handle(self, *args, **options):
        self.bot_properties = DefaultBotProperties()

        self.bot_properties.parse_mode = options["parse_mode"]
        self.bot_properties.allow_sending_without_reply = not options["do_not_send_without_reply"]
        {
            "large": self.bot_properties.link_preview_prefer_large_media,
            "small": self.bot_properties.link_preview_prefer_small_media,
            "disable": self.bot_properties.link_preview_is_disabled,
        }[options["link_preview"]] = True
        self.bot_properties.link_preview_show_above_text = options["link_preview_above_text"]

        async def start_polling(bot_token: str, skip_updates: bool) -> None:
            dp = self.setup_dispatcher()
            bot = Bot(bot_token, default=self.bot_properties)
            if skip_updates:
                await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)

        asyncio.run(start_polling(options["bot_api_key"], options["skip_updates"]))