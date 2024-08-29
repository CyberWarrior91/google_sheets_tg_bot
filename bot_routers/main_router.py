from aiogram import Router, types, F, html
from aiogram.filters.command import Command
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter
from .utils import bot
from aiogram.utils.deep_linking import create_start_link
from aiogram.enums.parse_mode import ParseMode

router = Router()

@router.message(Command("start"))
async def start_command(message: types.Message):
    text = "Добро пожаловать в бот по учету расходов в таблице Google Sheets!\n\n"\
            "Список команд:\n"\
            "🌟/table создание и управление таблицами с расходами\n"\
            "🌟/add_expense добавить новый расход в таблицу\n"\
            "🌟/this_month_expenses посмотреть общий расход по таблице за последний месяц\n"\
            "🌟/last_ten_expenses посмотреть последние 10 трат по таблице\n"
    await message.answer(text=text)

@router.message(StateFilter(None), Command(commands=["cancel"]))
@router.message(default_state, F.text.lower() == "отмена")
async def cmd_cancel_no_state(message: types.Message, state: FSMContext):
    await state.set_data({})
    await message.answer(
        text="Нечего отменять",
        reply_markup=types.ReplyKeyboardRemove()
    )


@router.message(Command(commands=["cancel"]))
@router.message(F.text.lower() == "отмена")
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Действие отменено",
        reply_markup=types.ReplyKeyboardRemove()
    )

# @router.message(F.text, Command("get_deep_link"))
# async def cmd_start(message: types.Message):
#     link = await create_start_link(bot=bot, payload="help")
#     await message.answer(
#         f"Hello, {html.bold(html.quote(message.from_user.username))}! Link: {link}.\n",
#         # f"And your deeplink is here: {deep_link}\n",
#         parse_mode=ParseMode.HTML)
