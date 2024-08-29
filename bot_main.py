import logging
import asyncio
import os
from aiogram import Dispatcher, types, Bot
from bot_routers.table_crud_operations import router as table_router
from bot_routers.other import router as router_other
from bot_routers.expense_crud_operations import router as expense_router
from bot_routers.main_router import router as main_router
# from bot_routers.utils import bot
from aiogram.utils.chat_action import ChatActionMiddleware
from bot_routers.middleware.auth_middleware import AuthorizationMiddleware
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN", None)



async def main():
    bot = Bot(token=BOT_TOKEN)

    dp = Dispatcher()
    dp.message.outer_middleware(AuthorizationMiddleware())
    dp.message.middleware(ChatActionMiddleware())
    await bot.set_my_commands(
        [   
            types.BotCommand(command="start", description="Главное меню бота"),
            types.BotCommand(command="table", description="Управлять таблицами с расходами"),
            types.BotCommand(command="add_expense", description="Добавить расход в таблицу"),
            types.BotCommand(command="this_month_expenses", description="Посмотреть расходы за этот месяц"),
            types.BotCommand(command="last_ten_expenses", description="Последние 10 трат в этом месяце"),
            # types.BotCommand(command="view_specific_month_expenses", description="Посмотреть расходы за определенный месяц"),
            ]
    )
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

    dp.include_routers(
        main_router, 
        table_router,
        expense_router,
        router_other
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError:
        print("Exit")
