from aiogram import types, Bot
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv
import os
from typing import List

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", None)
bot = Bot(token=BOT_TOKEN)

CANCEL_MESSAGE = 'Для отмены действия отправьте команду /cancel или напишите слово "отмена"'

def create_builder(spreadsheets: List[str]):
    builder = ReplyKeyboardBuilder()
    for s_name in spreadsheets:
        builder.add(types.KeyboardButton(text=str(s_name)))
    builder.adjust(3)
    return builder

async def show_tables_as_reply(
        spreadsheets_list: List[str], 
        message: types.Message, 
        state: FSMContext, 
        text: str,
        next_state: StatesGroup
        ):
    builder = create_builder(spreadsheets_list)
    await message.answer(
        text,
        reply_markup=builder.as_markup(
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )
    await state.update_data(tables=spreadsheets_list)
    await state.set_state(next_state)

async def table_name_false_input(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    builder = create_builder(user_data["tables"])
    await message.answer(
        "Таблица с таким именем не найдена!\n"
        "Пожалуйста, выберите таблицу из списка ниже:",\
        reply_markup=builder.as_markup(
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )
    await message.answer(CANCEL_MESSAGE)
