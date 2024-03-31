import functools

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
# from loguru import logger

from ..app.app import App
from ..handlers.support import Support
from ..keyboards import welcome_kb

router = Router(name=__name__)


@router.message(CommandStart())
async def command_start_handler(message: Message):
    await message.answer("Hello user!", reply_markup=welcome_kb.as_markup())


def casefold(action_enum):
    action_value = welcome_kb.get_action_value(action_enum).casefold()

    def decorator(func):
        @router.message(Command(action_value))
        @router.message(F.text.casefold() == action_value)
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        return wrapper

    return decorator


@casefold(welcome_kb.Action.HELP)
async def help_handler(
    message: Message,
):
    await message.answer(
        text="Help text! Use Reply markup keyboard to choose action",
        reply_markup=welcome_kb.as_markup(),
    )


@casefold(welcome_kb.Action.ASK)
async def ask_handler(
    message: Message,
    state: FSMContext,
):
    await state.set_state(Support.zero_level)
    await message.answer(text="Ask me smth!", reply_markup=ReplyKeyboardRemove())


@casefold(welcome_kb.Action.REPORT)
async def report_handler(
    message: Message,
    state: FSMContext,
):
    raise App.Report("{}")


@casefold(welcome_kb.Action.DONATE)
async def donate_handler(
    message: Message,
    state: FSMContext,
):
    await message.answer(text="Thank you!!! 💔", reply_markup=welcome_kb.as_markup())


@router.message(Command("cancel"))
@router.message(F.text.casefold() == "cancel")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    # logger.info(f"Cancelling state {current_state}")
    await state.clear()
    await message.answer(
        "Okay. Choose the next action please.",
        reply_markup=welcome_kb.as_markup(),
    )
