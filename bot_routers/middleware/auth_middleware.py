from aiogram import BaseMiddleware
from aiogram.types import Message
from database.db_crud_operations import  check_user_in_database
from typing import Callable, Dict, Any, Awaitable
from aiogram.utils.markdown import hlink
import os
from dotenv import load_dotenv

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

FASTAPI_HOST = os.getenv("FASTAPI_HOST", "http://127.0.0.1:8000")


class AuthorizationMiddleware(BaseMiddleware):

    async def __call__(self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        user = await self.is_user_authorized(user_id)
        if not user:
            auth_link = f"{FASTAPI_HOST}?telegram_id={user_id}"
            hyper_link = hlink("ССЫЛКА", auth_link)
            # If not, redirect to Google authorization flow 
            await event.answer(
                "Для начала использования бота, пожалуйста, авторизуйтесь через свой Google аккаунт: \n\n"
                f"{hyper_link}", parse_mode="HTML"
            )
        else:
            await handler(event, data)

    async def is_user_authorized(self, user_id: int):
        # Check if the user has an associated access token 
        # Replace this with your database query or token storage mechanism
        user = check_user_in_database(telegram_id=user_id)
        print(user)
        if not user:
          return None
        return user.access_token if user.access_token else None
