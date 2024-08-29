from database.get_db import get_async_session, get_session
from database.models import User, Spreadsheet, Sheet
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

def add_user_to_db(telegram_id: int):
    for session in get_session():
        new_user = User(telegram_id=telegram_id)
        session.add(new_user)
        session.commit()
        print("The user was added successfully")
        return new_user

def check_user_in_database(telegram_id: int):
    for session in get_session():
        user_in_db = session.scalars(
            select(User).where(
            User.telegram_id==telegram_id
            ).options(joinedload(User.spreadsheets))
        )
        user = user_in_db.first()
        return user if user else None

# async def check_user_in_db(telegram_id: int):
#     async for session in get_async_session():
#         user_in_db = await session.scalars(
#             select(User).where(
#                 User.telegram_id==telegram_id
#                 ).options(joinedload(User.spreadsheets))
#         )
#         user = user_in_db.first()
#         return user if user else None

def add_token_to_user(telegram_id: int, token: str):
    for session in get_session():
        user_in_db = session.scalars(
            select(User).where(
                User.telegram_id==telegram_id)
        )
        user = user_in_db.first()
        user.access_token = token
        session.commit()
        print("The token was added successfully")
        return user

async def add_spreadsheet_to_db(google_unique_id: str, name: str, user_telegram_id: int):
    async for session in get_async_session():
        new_spdsheet = Spreadsheet(
            google_unique_id=google_unique_id,
            name=name,
            user_telegram_id=user_telegram_id
        )
        session.add(new_spdsheet)
        await session.commit()
        print("The spreadsheet was added successfully")
        return new_spdsheet

async def add_sheet_to_db(google_unique_id: int, name: str, spreadsheet_id: str):
    async for session in get_async_session():
        new_sheet = Sheet(
            google_unique_id=google_unique_id,
            name=name,
            spreadsheet_id=spreadsheet_id
        )
        session.add(new_sheet)
        await session.commit()
        print("The sheet was added successfully")
        return new_sheet


async def get_spreadsheets_by_user(user_telegram_id: int):
    curr_user = await check_user_in_db(telegram_id=user_telegram_id)
    if curr_user:
        return [s.name for s in curr_user.spreadsheets]
    else:
        return []

async def get_sheets_by_spreadsheet_id(s_id: str):
    async for session in get_async_session():
        spreadsheet_in_db = await session.scalars(
            select(Spreadsheet).where(
                Spreadsheet.google_unique_id==s_id).options(
                    joinedload(Spreadsheet.sheets)
                )
        )
        spreadsheet = spreadsheet_in_db.first()
        if spreadsheet is None:
            return [None]
        return [sheet.name for sheet in spreadsheet.sheets]


async def get_spreadsheet_id_by_name(name: str):
    async for session in get_async_session():
        s_in_db = await session.scalars(select(Spreadsheet).where(Spreadsheet.name==name))
        spreadsheet = s_in_db.first()
        if spreadsheet:
            return spreadsheet.google_unique_id
        return None

async def edit_spreadsheet_name_in_db(id: str, new_name: str):
    async for session in get_async_session():
        s_in_db = await session.scalars(select(Spreadsheet).where(Spreadsheet.google_unique_id==id))
        spreadsheet = s_in_db.first()
        spreadsheet.name = new_name
        await session.commit()
        print("The spreadsheet name was changed successfully")

async def delete_spreadsheet_from_db(id: str):
    async for session in get_async_session():
        s_in_db = await session.scalars(select(Spreadsheet).where(Spreadsheet.google_unique_id==id))
        spreadsheet = s_in_db.first()
        if spreadsheet is None:
            print("Таблица с расходами не найдена или уже удалена")
            return False
        await session.delete(spreadsheet)
        print("Таблица успешно удалена из базы данных")
        await session.commit()
        return True
