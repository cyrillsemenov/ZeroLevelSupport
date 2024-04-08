import json

import yaml
from aiogram import F, Router
from aiogram.filters import ExceptionTypeFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.types.error_event import ErrorEvent
from asgiref.sync import sync_to_async

# from loguru import logger
from pydantic import ValidationError

from ..app.app import App
from ..form import Form
from ..keyboards import welcome_kb
from ..models import Report

router = Router()


class FormFull(Exception):
    pass


class CollectReport(StatesGroup):
    asking = State()
    finishing = State()


REPORT_TEXT_PREFIX = 'Получен репорт\n====\n<pre language="yaml">\n'
REPORT_TEXT_SUFFIX = "</pre>\n===="


# https://github.com/dyadyaJora/tg-webapp-shutdown-report
@router.message(F.web_app_data)
async def enter_date(message: Message) -> None:
    data = message.web_app_data.data
    report = await sync_to_async(Report.from_json)(data, status="DOWN")
    await message.answer(
        REPORT_TEXT_PREFIX
        + yaml.dump(await sync_to_async(report.to_dict)(), allow_unicode=True)
        + REPORT_TEXT_SUFFIX,
        # reply_markup=get_report_callback_keyboard(),
    )


@router.error(ExceptionTypeFilter(App.Report), F.update.message.as_("message"))
async def handle_report(event: ErrorEvent, message: Message, state: FSMContext):
    report_raw_data = str(event.exception)

    await state.set_state(CollectReport.asking)

    data = await state.update_data(detector=Form(**json.loads(report_raw_data)))
    # logger.debug("Catch {data}", data=data)
    # logger.debug("Data {data}", data=data["detector"].data)
    q, a = next(data["detector"].get_next_empty_field())
    if q is None:
        raise FormFull
    await state.update_data(answer=a)

    await message.answer(q, reply_markup=ReplyKeyboardRemove())


@router.message(CollectReport.asking)
async def process_answer(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    data["answer"](message.text)
    # logger.debug("Ask {data}", data=data)
    q, a = next(data["detector"].get_next_empty_field())
    if q is None:
        raise FormFull
    await state.update_data(answer=a)
    await message.answer(q, reply_markup=ReplyKeyboardRemove())


@router.error(ExceptionTypeFilter(FormFull), F.update.message.as_("message"))
async def handle_stop_iteration(event: ErrorEvent, message: Message, state: FSMContext):
    data = await state.get_data()
    p = data["detector"].data
    # logger.debug("Full {data}", data=data)
    await state.clear()
    report = f"""All done! Your report is:

    <b>URL:</b> <code><a href='{p.url}'>{p.url}</a></code>
    <b>Geo:</b> <code>{p.geo}</code>
    <b>Provider:</b> <code>{p.provider}</code>
    <b>Message:</b> <code>{p.message}</code>
    <b>Time:</b> <code>{p.time.strftime('%B %d, %Y, %H:%M:%S')}</code>"""
    await message.answer(report, reply_markup=welcome_kb.as_markup())


@router.error(ExceptionTypeFilter(ValidationError), F.update.message.as_("message"))
async def handle_validation_error(
    event: ErrorEvent, message: Message, state: FSMContext
):
    await message.answer(str(event.exception), reply_markup=ReplyKeyboardRemove())
