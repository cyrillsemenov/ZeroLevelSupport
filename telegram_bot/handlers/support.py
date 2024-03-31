import logging

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
)
from aiogram.types.error_event import ErrorEvent

from ..app.app import App
from ..keyboards import welcome_kb

app = App()
router = Router()


class Support(StatesGroup):
    zero_level = State()
    first_level = State()


@router.message(Support.zero_level)
@flags.chat_action(initial_sleep=2, action=ChatAction.TYPING, interval=3)
async def process_question(message: Message, state: FSMContext) -> None:
    await state.update_data(question=message.text)
    await state.set_state(Support.first_level)
    await message.answer(
        f"{app.find_answer(message.text)}\n\n<b>Was this answer helpful?</b>",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Yes"),
                    KeyboardButton(text="No"),
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
    )


async def go_to_the_first_level(message: Message, state: FSMContext):
    data = await state.get_data()
    logging.info(data["question"])
    await state.clear()
    await message.answer(
        "Connecting you to an operator...",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(Support.first_level, F.text.casefold().in_({"no", "n", "0"}))
async def process_not_happy(message: Message, state: FSMContext) -> None:
    # data = await state.get_data()
    # Remove original data["question"] to index embeddings (punish)
    await go_to_the_first_level(message, state)


@router.error(ExceptionTypeFilter(App.NotFound), F.update.message.as_("message"))
async def handle_not_found(event: ErrorEvent, message: Message, state: FSMContext):
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
