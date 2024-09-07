from aiogram import Router, F, types
from aiogram.filters.command import Command
from aiogram.utils.markdown import hlink
import os
from dotenv import load_dotenv

load_dotenv()

FASTAPI_HOST = os.getenv("FASTAPI_HOST", "http://127.0.0.1:8000")

router = Router()

@router.message(Command("manage_google_acc"))
async def manage_account(message: types.Message):
    user_id = message.from_user.id
    auth_link = f"{FASTAPI_HOST}?telegram_id={user_id}"
    google_link = hlink("ССЫЛКА", auth_link)
    await message.answer(
        "Для управления доступом к своему Google аккаунту, перейдите по ссылке ниже:\n\n"
        f"{google_link}", parse_mode="HTML"
    )


@router.message(F.text)
async def reply_to_other(message: types.Message):
    await message.answer(
        "Я не знаю такой команды:(\n"
        "Отправьте команду /start для получения списка доступных команд"
    )