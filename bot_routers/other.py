from aiogram import Router, F, types


router = Router()

@router.message(F.text)
async def reply_to_other(message: types.Message):
    await message.answer(
        "Я не знаю такой команды:(\n"
        "Отправьте команду /start для получения списка доступных команд"
    )