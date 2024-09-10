from aiogram import Router, types
import datetime
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db_crud_operations import (
    get_spreadsheets_by_user,
    get_spreadsheet_id_by_name,
    get_sheets_by_spreadsheet_id,
    add_sheet_to_db
)
from google_sheets.google_sheets_operations import (
    append_new_values,
    show_last_ten_expenses,
    show_this_month_expenses,
    create_new_sheet
)
from .utils import (
    table_name_false_input,
    show_tables_as_reply
)

router = Router()


class Expense(StatesGroup):
    waiting_for_add_expense = State()
    waiting_for_expense_item = State()
    waiting_for_expense_amount = State()
    show_expenses_choose_table = State()
    show_monthly_expenses_choose_table = State()


@router.message(Command("add_expense"))
async def add_new_expense_start(message: types.Message, state: FSMContext):
    user_spreadsheets = get_spreadsheets_by_user(message.from_user.id)
    if user_spreadsheets:
        msg = "Выберите таблицу, к которой хотите добавить новую статью расхода:"
        await show_tables_as_reply(
            spreadsheets_list=user_spreadsheets,
            message=message,
            state=state,
            text=msg,
            next_state=Expense.waiting_for_add_expense
        )
    else:
        await message.answer(
            "У вас нет ни одной таблицы с расходами!\n\n"
            "Чтобы добавить новую таблицу, отправьте команду /table, а затем \n"
            'нажмите на "Создать новую табличку с расходами"'
        )

@router.message(Expense.waiting_for_add_expense)
async def add_expense_item_start(message: types.Message, state: FSMContext):
    s_id = get_spreadsheet_id_by_name(name=message.text)
    if s_id:
        await state.update_data(spreadsheet_id=s_id)
        msg = 'Пожалуйста, укажите статью расходов.\n'\
            'Пример: "магазин", "ресторан", "коммуналка"'
        await message.answer(text=msg)
        await state.set_state(Expense.waiting_for_expense_item)
    else:
        await table_name_false_input(message, state)

@router.message(Expense.waiting_for_expense_item)
async def add_new_expense_item(message: types.Message, state: FSMContext):
    if len(message.text) > 50:
        await message.answer("Слишком длинная статья расходов, попробуйте описать ее короче!")
        return
    await state.update_data(expense_item=message.text)
    await message.answer(
        f'Ваша статья расходов: "{message.text}". Пожалуйста, введите сумму расхода.\n'
        'Пример: 2000, 350, 115.45'
    )
    await state.set_state(Expense.waiting_for_expense_amount)

@router.message(Expense.waiting_for_expense_amount)
async def add_new_expense_amount(message: types.Message, state: FSMContext):
    if not message.text.isdecimal():
        await message.answer(
            "Для добавления расхода, введите, пожалуйста, введите любое положительное число"
        )
        return
    if len(str(message.text)) > 15:
        await message.answer(
            f"Слишком большая сумма расхода, вы уверены что столько потратили?😁"        
        )
        return
    await state.update_data(expense_amount=message.text)
    user_data = await state.get_data()
    await message.answer(f'Ваша сумма расхода: {user_data["expense_amount"]}.\n')
    base_spreadsheet_id = user_data.get("spreadsheet_id", None)
    sheets = get_sheets_by_spreadsheet_id(s_id=base_spreadsheet_id)
    todays_month_and_year = datetime.datetime.today().strftime("%m/%Y")
    if todays_month_and_year not in sheets:
        sheet_id, sheet_name = create_new_sheet(
            message.from_user.id,
            spreadsheet_id=base_spreadsheet_id,
            title=todays_month_and_year
        )
        sheets.append(sheet_name)
        add_sheet_to_db(
            google_unique_id=sheet_id, 
            name=sheet_name, 
            spreadsheet_id=base_spreadsheet_id
        )
    append_new_values(
        message.from_user.id,
        spreadsheet_id=base_spreadsheet_id, 
        values_list=[user_data.get("expense_item", ""),
        user_data.get("expense_amount", "")],
        sheet_name=sheets[-1]
    )
    await message.answer(
        'Статья расходов была успешно добавлена!\n\n'
        'Чтобы посмотреть последние 10 расходов, отправьте команду /last_ten_expenses\n'
        'Чтобы посмотреть расходы за этот месяц, отправьте команду /this_month_expenses\n'
        'Чтобы добавить еще один расход, вызовите команду /add_expense\n'
    )
    await state.clear()

@router.message(Command("last_ten_expenses"))
async def view_last_ten_expenses_start(message: types.Message, state: FSMContext):
    user_spreadsheets = get_spreadsheets_by_user(message.from_user.id)
    if user_spreadsheets:
        msg = "Выберите таблицу, по которой хотите посмотреть последние 10 расходов:"
        await show_tables_as_reply(
            spreadsheets_list=user_spreadsheets,
            message=message,
            state=state,
            text=msg,
            next_state=Expense.show_expenses_choose_table
        )
    else:
        await message.answer(
            "У вас нет ни одной таблицы с расходами!\n\n"
            "Чтобы добавить новую таблицу, выберите в главном меню команду\n"
            '"Создать новую табличку с расходами"'
        )


@router.message(Expense.show_expenses_choose_table)
async def view_last_ten_expenses_success(message: types.Message, state: FSMContext):
    table_id = get_spreadsheet_id_by_name(name=message.text)
    if table_id:
        sheets = get_sheets_by_spreadsheet_id(s_id=table_id)
        result = show_last_ten_expenses(
            message.from_user.id,
            table_id, 
            sheet_name=sheets[-1]
        )
        if result is None:
            await message.answer("По этой таблице пока нет расходов!")
            return
        await message.answer(
             f'Вот ваши последние 10 транзакций в этом месяце:\n\n{result}'
        )
        await state.clear()
    else:
        await table_name_false_input(message, state)

@router.message(Command("this_month_expenses"))
async def view_this_month_expenses_start(message: types.Message, state: FSMContext):
    user_spreadsheets = get_spreadsheets_by_user(message.from_user.id)
    if user_spreadsheets:
        msg = "Выберите таблицу, по которой хотите посмотреть общий расход за последний месяц:"
        await show_tables_as_reply(
            spreadsheets_list=user_spreadsheets,
            message=message,
            state=state,
            text=msg,
            next_state=Expense.show_monthly_expenses_choose_table
        )
    else:
        await message.answer("У вас нет ни одной таблицы с расходами!\n\n"
                             "Чтобы добавить новую таблицу, выберите в главном меню команду\n"
                             '"Создать новую табличку с расходами"')

@router.message(Expense.show_monthly_expenses_choose_table)
async def view_this_month_expenses_success(message: types.Message, state: FSMContext):
    table_id = get_spreadsheet_id_by_name(name=message.text)
    if table_id:
        sheets = get_sheets_by_spreadsheet_id(s_id=table_id)    
        result = show_this_month_expenses(
            message.from_user.id,
            table_id, 
            sheet_name=sheets[-1]
        )
        await message.answer(
             f"Ваши расходы за этот месяц: {result}"
        )
    else:
        await table_name_false_input(message, state)
