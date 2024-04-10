import logging
import os

from aiogram import F, Router, flags
from aiogram.enums import ChatAction
from aiogram.filters import ExceptionTypeFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    WebAppInfo,
)
from aiogram.types.error_event import ErrorEvent

from question_app.models import KnowledgeBase
from question_app.utils import Transformer

from ..app.app import App
from ..keyboards import welcome_kb

logger = logging.getLogger(__name__)

app = App()
router = Router()


class Support(StatesGroup):
    zero_level = State()
    first_level = State()


@router.message(Support.zero_level)
@flags.chat_action(initial_sleep=2, action=ChatAction.TYPING, interval=3)
async def process_question(message: Message, state: FSMContext) -> None:
    transformer = await Transformer.a_get()
    articles_similarity = await transformer.a_find_n_similar(message.text, 3)
    flags = {q: transformer.get_flags(q) for q, _ in articles_similarity}
    if not articles_similarity:
        await state.update_data(question=message.text)
        await state.set_state(Support.first_level)
        raise app.NotFound()
    elif articles_similarity[0][1] >= transformer.consider_similar:
        answer = await KnowledgeBase.objects.filter(
            question=articles_similarity[0][0]
        ).afirst()
        anwer_flags = flags.get(answer.question, [])
        if anwer_flags:
            if "Report" in anwer_flags:
                await state.clear()
                await message.answer(
                    "Хотите сообщить о проблеме?",
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=[
                            [
                                KeyboardButton(
                                    text="Заполнить анкету",
                                    web_app=WebAppInfo(url=os.getenv("WEB_APP_URL")),
                                )
                            ],
                            [KeyboardButton(text="Cancel")],
                        ]
                    ),
                )
                return
        await message.answer(
            f"{answer.answer}\n\n<b>Так же предлагаю прочитать ответы вот на эти вопросы:</b>",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    # [
                    #     KeyboardButton(text="Yes"),
                    #     KeyboardButton(text="No"),
                    # ],
                    *[
                        [KeyboardButton(text=q)]
                        for q, _ in articles_similarity[1:]
                        if "Do not suggest" not in flags.get(q, [])
                    ],
                    [KeyboardButton(text="Cancel")],
                ],
                resize_keyboard=True,
                one_time_keyboard=True,
            ),
        )
    else:
        await message.answer(
            "<b>Maybe you would find one of theese articles useful?</b>",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    *[
                        [KeyboardButton(text=q)]
                        for q, _ in articles_similarity
                        if "Do not suggest" not in flags.get(q, [])
                    ],
                    [KeyboardButton(text="🚫 Нет, соедини меня с оператором")],
                    [KeyboardButton(text="Cancel")],
                ],
                resize_keyboard=True,
                one_time_keyboard=True,
            ),
        )

    # await state.update_data(question=message.text)
    # await state.set_state(Support.first_level)


async def go_to_the_first_level(message: Message, state: FSMContext):
    data = await state.get_data()
    logger.info(data["question"])
    await state.clear()
    await message.answer(
        "Передали ваш вопрос оператору...",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.error(ExceptionTypeFilter(App.NotFound), F.update.message.as_("message"))
async def handle_not_found(event: ErrorEvent, message: Message, state: FSMContext):
    await go_to_the_first_level(message, state)


@router.message(Support.first_level, F.text.casefold().in_({"no", "n", "0"}))
async def process_not_happy(message: Message, state: FSMContext) -> None:
    # data = await state.get_data()
    # Remove original data["question"] to index embeddings (punish)
    await go_to_the_first_level(message, state)


@router.message(Support.first_level, F.text.casefold().in_({"yes", "y", "1"}))
async def process_like_write_bots(message: Message, state: FSMContext) -> None:
    # data = await state.get_data()
    # Add original data["question"] to index embeddings (praise)
    await state.clear()
    await message.reply(
        "Cool! What you want to do next?",
        reply_markup=welcome_kb.as_markup(),
    )


@router.message(Support.first_level)
async def process_unknown_write_bots(message: Message) -> None:
    await message.reply("I don't understand you :(")
