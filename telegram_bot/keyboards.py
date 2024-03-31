from __future__ import annotations

from enum import Enum
import os

from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardMarkup


class WelcomeKb:
    class Action(Enum):
        HELP = "help"
        ASK = "ask"
        REPORT = "report"
        DONATE = "donate"

    @staticmethod
    def get_action_value(action: Action) -> str:
        """Get the casefolded value of the specified action."""
        return action.value.casefold()

    def __init__(self) -> None:
        self.kb = ReplyKeyboardMarkup(
            # keyboard=[
            #     [KeyboardButton(text=action.value.title())]
            #     for action in WelcomeKb.Action
            # ],
            keyboard=[
                [KeyboardButton(text=WelcomeKb.Action.HELP.value.title())],
                [
                    KeyboardButton(text=WelcomeKb.Action.ASK.value.title()),
                    KeyboardButton(
                        text=WelcomeKb.Action.REPORT.value.title(),
                        web_app=WebAppInfo(url=os.getenv("WEB_APP_URL"))
                    ),
                ],
                [KeyboardButton(text=WelcomeKb.Action.DONATE.value.title())],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )

    def as_markup(self, **kwargs) -> ReplyKeyboardMarkup:
        return self.kb


welcome_kb = WelcomeKb()
