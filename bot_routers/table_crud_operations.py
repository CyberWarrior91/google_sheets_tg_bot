from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.command import Command
from aiogram.utils.markdown import hlink
from google_sheets.google_sheets_operations import (
    create_new_spreadsheet, 
    get_spreadsheet_url,
    change_spreadsheet_name,
    delete_spreadsheet_from_sheets,
    get_sheet
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from .utils import (
    table_name_false_input,
    CANCEL_MESSAGE,
    show_tables_as_reply
)
from database.db_crud_operations import (
    add_spreadsheet_to_db,
    add_sheet_to_db,
    add_user_to_db, 
    check_user_in_database,
    get_spreadsheets_by_user,
    get_spreadsheet_id_by_name,
    edit_spreadsheet_name_in_db,
    delete_spreadsheet_from_db
)

router = Router()

class Table(StatesGroup):
    # Create:
    create_waiting_for_title = State()
    # Edit:
    change_title_choose_old_name = State()
    wait_for_new_title = State()
    # View:
    view_table_choose = State()
    # Delete:
    delete_choose_table = State()

@router.message(Command("table"))
async def table_command(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="Создать новую табличку с расходами", callback_data="add_table")
    )
    builder.row(
        types.InlineKeyboardButton(text="Изменить имя таблицы", callback_data="edit_table"),
        types.InlineKeyboardButton(text="Получить ссылку на таблицу", callback_data="view_table")
        
    )
    builder.row(
        types.InlineKeyboardButton(text="Удалить таблицу", callback_data="delete_table")
    )
    await message.reply("Выберите, что хотите сделать:", reply_markup=builder.as_markup())

@router.callback_query(F.data == "add_table")
async def create_new_table(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Пожалуйста, укажите имя для таблицы с расходами.\n'
                                  'Пример: "Расходы по карте Сбер"\n')
    await callback.message.answer(CANCEL_MESSAGE)
    await callback.answer()
    await state.set_state(Table.create_waiting_for_title)

@router.message(Table.create_waiting_for_title)
async def parse_title(message: types.Message, state: FSMContext):
    title = message.text
    if len(title) > 35:
        await message.answer("Слишком длинное название для таблицы!\n"
                             "Пожалуйста, придумайте имя покороче (до 35 символов)")
        return
    user_id = message.from_user.id
    spreadsheet_id = await create_new_spreadsheet(user_id, title=title)
    if check_user_in_database(user_id) is None:
        await add_user_to_db(telegram_id=user_id)
    await add_spreadsheet_to_db(
        google_unique_id=spreadsheet_id,
        name=title,
        user_telegram_id=user_id
    )
    sheet_id, sheet_name = await get_sheet(user_id, spreadsheet_id)
    await add_sheet_to_db(google_unique_id=sheet_id, name=sheet_name, spreadsheet_id=spreadsheet_id)
    table_url = await get_spreadsheet_url(user_id, spreadsheet_id)
    hyper_link = hlink("ссылка", table_url)
    await message.answer(
        f'Название таблицы: "{title}". Таблица сохранена!\n\n'
        f'Вот {hyper_link} на вашу таблицу в Google Sheets\n\n'
        "Чтобы добавить свой первый расход, отправьте команду /add_expense\n"
        "\nЧтобы вернуться в главное меню, отправьте команду /start\n"
        "Чтобы управлять таблицами, отправьте команду /table",
        parse_mode="HTML"
    )
    await state.set_state(state=None)

@router.callback_query(F.data == "edit_table")
async def change_table_title_start(callback: types.CallbackQuery, state: FSMContext):
    user_spreadsheets = await get_spreadsheets_by_user(callback.from_user.id)
    if user_spreadsheets:
        msg = "Пожалуйста, выберите таблицу, которую хотите переименовать:\n"
        await show_tables_as_reply(
            spreadsheets_list=user_spreadsheets,
            message=callback.message,
            state=state,
            text=msg,
            next_state=Table.change_title_choose_old_name
        )
    else:
        await callback.message.answer("Таблицы с расходами не найдены!"
                       "Чтобы добавить новую таблицу, выберите в главном меню команду\n"
                       '"Создать новую табличку с расходами"')
    await callback.answer()

@router.message(Table.change_title_choose_old_name)
async def change_title_choose_table(message: types.Message, state: FSMContext):
    title = message.text
    s_id = await get_spreadsheet_id_by_name(name=title)
    if s_id is None:
        await table_name_false_input(message, state)
    else:
        await state.update_data(spreadsheet_id=s_id)
        await message.answer(
            f'Таблица: "{title}"\n'
            "Теперь введите новое имя для таблицы", 
            reply_markup=types.ReplyKeyboardRemove()
        )
        await message.answer(CANCEL_MESSAGE)
        await state.set_state(Table.wait_for_new_title)

@router.message(Table.wait_for_new_title)
async def change_title_success(message: types.Message, state: FSMContext):
    new_title = message.text
    if len(new_title) > 35:
        await message.answer("Слишком длинное название для таблицы!\n"
                             "Пожалуйста, придумайте имя покороче (до 35 символов)")
    else:
        user_data = await state.get_data()
        await message.answer(f'Новое имя для таблицы: "{new_title}"')
        s_id = user_data["spreadsheet_id"]
        await change_spreadsheet_name(message.from_user.id, s_id, new_title)
        await edit_spreadsheet_name_in_db(id=s_id, new_name=new_title)
        await message.answer(f'Таблица была успешно переименована!')
        await message.answer(
        "Чтобы вернуться в главное меню бота, отправьте команду /start"
        )
        await state.clear()

@router.callback_query(F.data == "view_table")
async def view_expense_table_start(callback: types.CallbackQuery, state: FSMContext):
    user_spreadsheets = await get_spreadsheets_by_user(callback.from_user.id)
    if user_spreadsheets:
        msg = "Пожалуйста, выберите таблицу, по которой хотите получить ссылку:\n"
        await show_tables_as_reply(
            spreadsheets_list=user_spreadsheets,
            message=callback.message,
            state=state,
            text=msg,
            next_state=Table.view_table_choose
        )
        await callback.message.answer(CANCEL_MESSAGE)
    else: 
        error_msg = "Ни одна таблица с расходами не найдена!"
        await callback.message.answer(error_msg)
    await callback.answer()

@router.message(Table.view_table_choose)
async def view_expense_table(message: types.Message, state: FSMContext):
    table_name = message.text
    spreadsheet_id = await get_spreadsheet_id_by_name(name=table_name)
    if spreadsheet_id:
        table_url = await get_spreadsheet_url(message.from_user.id, spreadsheet_id)
        hyper_link = hlink("ссылка", table_url)
        msg = f'Вот ваша {hyper_link} на таблицу!'
        await message.answer(msg, parse_mode="HTML")
        await state.clear()
    else:
        await table_name_false_input(message, state)

@router.callback_query(F.data == "delete_table")
async def delete_table_start(callback: types.CallbackQuery, state: FSMContext):
    user_spreadsheets = await get_spreadsheets_by_user(callback.from_user.id)
    if user_spreadsheets:
        msg = "Пожалуйста, выберите таблицу, которую хотите удалить:\n"
        await show_tables_as_reply(
            spreadsheets_list=user_spreadsheets,
            message=callback.message,
            state=state,
            text=msg,
            next_state=Table.delete_choose_table
        )
        await callback.message.answer(CANCEL_MESSAGE)
    else:
        error_msg = "Ни одна таблица с расходами не найдена!"
        await callback.message.answer(error_msg)
    await callback.answer()


@router.message(Table.delete_choose_table)
async def delete_table_start(message: types.Message, state: FSMContext):
    table_name = message.text
    table_id = await get_spreadsheet_id_by_name(table_name)
    if not table_id:
        await table_name_false_input(message, state)
    else:
        msg = f'Таблица "{table_name}"\n\n'\
                "Вы уверены, что хотите ее удалить?"
        builder = InlineKeyboardBuilder()
        builder.add(
            types.InlineKeyboardButton(text="Да", callback_data="Yes"),
            types.InlineKeyboardButton(text="Нет, я передумал(а)", callback_data="No")
        )
        await message.answer(text=msg, reply_markup=builder.as_markup())
        await state.update_data(table=table_name)

@router.callback_query(F.data=="No")
async def delete_no_answer(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Нет проблем!\n\nЧтобы вернуться в главное меню, отправьте команду /start")
    await state.clear()
    await callback.answer()

@router.callback_query(F.data=="Yes")
async def delete_yes_answer(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    spreadsheet_id = await get_spreadsheet_id_by_name(user_data["table"])
    if await delete_spreadsheet_from_db(spreadsheet_id) is True:
        if await delete_spreadsheet_from_sheets(callback.from_user.id, spreadsheet_id) is True:
            await callback.message.answer("Таблица была успешно удалена!")
        else:
            await callback.message.answer(
                "Таблица не найдена или уже была удалена из Google Sheets!\n\n"
                "Она будет удалена из списка ваших таблиц в меню бота"
            )
    else:
        await callback.message.answer("Таблица не найдена или уже была удалена!")
    await callback.message.answer(
        "Чтобы вернуться в главное меню бота, отправьте команду /start"
    )
    await callback.answer()
    await state.clear()

