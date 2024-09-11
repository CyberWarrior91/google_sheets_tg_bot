import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .oauth import SCOPES
from google.oauth2.credentials import Credentials
from database.db_crud_operations import check_user_in_database
import json
import pytz


def get_google_sheets_service(user_telegram_id: int):
    """Returns a Google Sheets API service object."""
    user = check_user_in_database(user_telegram_id)
    if user and user.access_token:
      token = json.loads(user.access_token)
      creds = Credentials.from_authorized_user_info(token, SCOPES)
      print(creds)
      return build('sheets', 'v4', credentials=creds)
    return None

def create_new_spreadsheet(user_id: int, title: str) -> str|None:
  """Creates new spreadsheet in Google Sheets service with a specified name"""
  """Also, adds a first line for the table in the first sheet, makes it bold"""
  """and renames it with the current month and year by this sample: '01/2000'"""
  try:
    service = get_google_sheets_service(user_id)
    spreadsheet = {"properties": {"title": title}}
    spreadsheet = (
        service.spreadsheets()
        .create(body=spreadsheet, fields="spreadsheetId")
        .execute()
    )
    new_spreadsheet_id = spreadsheet.get('spreadsheetId')
    print(f"Spreadsheet id: {new_spreadsheet_id}")
    month_and_year = datetime.datetime.today().strftime("%m/%Y")
    requests = []
    requests.append(
      {"updateSheetProperties": 
       {"properties": 
        {
          "title": month_and_year
          }, 
        "fields": "title"
        }
      }
    )
    body = {"requests": requests}
    service.spreadsheets().batchUpdate(spreadsheetId=new_spreadsheet_id, body=body).execute()
    fill_first_row(user_id, new_spreadsheet_id)
    bold_first_row(user_id, new_spreadsheet_id)
    return new_spreadsheet_id
  except HttpError as error:
    print(f"An error occurred: {error}")
    return error

def bold_first_row(user_id: int, spreadsheet_id: str, sheet_id: int = 0):
  try:
    service = get_google_sheets_service(user_id)
    requests = [
      {
        "updateCells": {
          "rows": [
            {
              "values": [
                
                {"textFormatRuns": [{"format": {"bold": True}}]},
                {"textFormatRuns": [{"format": {"bold": True}}]},
                {"textFormatRuns": [{"format": {"bold": True}}]},
                {},
                {"textFormatRuns": [{"format": {"bold": True}}]},
              ]
            },
              
          ],
          "range": {
            "startColumnIndex": 0,
            "endColumnIndex": 5,
            "startRowIndex": 0,
            "endRowIndex": 2,
            "sheetId": sheet_id
          },
          "fields": "textFormatRuns"
        }
      }
    ]
    body = {"requests": requests}
    service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
    print("Formatting is completed")
  except HttpError as error:
    print(f"An error occurred: {error}")
    return error


def fill_first_row(user_id: int, spreadsheet_id: str, sheet_name: str = ''):
  try:
    service = get_google_sheets_service(user_id)
    values = ["Дата", "Расход", "Сумма", "Всего за месяц"]
    data = [
        {"range": f"{sheet_name}!A1:C1", "values": [values[:-1]]},
        {"range": f"{sheet_name}!E1", "values": [values[-1:]]}
    ]
    body = {"valueInputOption": "USER_ENTERED", "data": data}
    service.spreadsheets().values().batchUpdate(
      spreadsheetId=spreadsheet_id, 
      body=body
      ).execute()
    body = {"values": [["=SUM(C:C)"]]}
    service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!E2",
            valueInputOption="USER_ENTERED",
            body=body,
            ).execute()
    print("Values have been updated")
  except HttpError as error:
    print(f"An error occurred: {error}")
    return error

def get_spreadsheet_url(user_id: int, spreadsheet_id: str):
  try:
    service = get_google_sheets_service(user_id)
    result = (
        service.spreadsheets()
        .get(spreadsheetId=spreadsheet_id)
        .execute()
    )
    return result.get("spreadsheetUrl", None)
  except HttpError as error:
    print(f"An error occurred: {error}")
    return error
  
def change_spreadsheet_name(user_id: int, spreadsheet_id: str, title: str):
  """Changes the title of a spreadsheet"""
  try:
    service = get_google_sheets_service(user_id)
    requests = []
    requests.append(
        {
          "updateSpreadsheetProperties": {
              "properties": {"title": title},
              "fields": "title",
          }
        }
    )
    body = {"requests": requests}
    service.spreadsheets().batchUpdate(
      spreadsheetId=spreadsheet_id, 
      body=body).execute()
    return
  except HttpError as error:
    print(f"An error occurred: {error}")
    return error

def append_new_values(
    user_id: int,
    spreadsheet_id: str, 
    values_list: list,
    sheet_name: str,
    range_name:str = "A2",
    ):
  """Adds a list of values to the specified range of a sheet"""
  try:
    service = get_google_sheets_service(user_id)
    msc_tz = pytz.timezone("Europe/Moscow")
    date = datetime.datetime.now(msc_tz).strftime("%d-%m-%Y %H:%M")
    values_list.insert(0, date)
    body = {"values": [values_list]}
    result = (
        service.spreadsheets()
        .values()
        .append(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!{range_name}",
            valueInputOption="USER_ENTERED",
            body=body,
        )
        .execute()
    )
    print(f"{(result.get('updates').get('updatedCells'))} cells appended.")
    return result
  except HttpError as error:
    print(f"An error occurred: {error}")
    return error

def create_new_sheet(user_id: int, spreadsheet_id: str, title: str):
  """Creates new sheet for a specified spreadsheet"""
  try:
    service = get_google_sheets_service(user_id)
    requests = []
    requests.append(
        {
            "addSheet": {
                "properties": {"title": f'{title}'},
            }
        }
    )
    body = {"requests": requests}
    response = (
        service.spreadsheets()
        .batchUpdate(spreadsheetId=spreadsheet_id, body=body)
        .execute()
    )
    result = response.get("replies")[0].get('addSheet').get('properties')
    sheet_id, sheet_name = result.get("sheetId", None), result.get("title", None)
    fill_first_row(user_id, spreadsheet_id=spreadsheet_id, sheet_name=sheet_name)
    bold_first_row(user_id, spreadsheet_id=spreadsheet_id, sheet_id=sheet_id)
    print(f"Sheet {sheet_id} added")
    print(f"Sheet name is {sheet_name}")
    return sheet_id, sheet_name
  except HttpError as error:
    print(f"An error occurred: {error}")
    return error

def get_sheet(user_id: int, spreadsheet_id: str):
  """Gets the first default sheet of a spreadsheet"""
  try:
    service = get_google_sheets_service(user_id)
    result = (
        service.spreadsheets()
        .get(spreadsheetId=spreadsheet_id)
        .execute()
    )
    sheet_info = result.get("sheets")[0].get("properties")
    if sheet_info:
      sheet_id, sheet_name = sheet_info.get("sheetId", None), sheet_info.get("title", None)
      print(sheet_id, sheet_name)
      return sheet_id, sheet_name
    else:
      return None
  except HttpError as error:
    print(f"An error occurred: {error}")
    return error

def show_this_month_expenses(user_id: int, spreadsheet_id: str, sheet_name: str):
  try:
    service = get_google_sheets_service(user_id)
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=f"{sheet_name}!E2")
        .execute()
    )
    rows = result.get("values", [])
    if rows:
      print(rows[0][0])
      return rows[0][0]
    else:
      print("No value here")
  except HttpError as error:
    print(f"An error occurred: {error}")
    return error
  
def show_last_ten_expenses(user_id: int, spreadsheet_id: str, sheet_name: str) -> str|None:
  try:
    service = get_google_sheets_service(user_id)
    try:
      result = (
          service.spreadsheets()
          .values()
          .get(spreadsheetId=spreadsheet_id, range=f"{sheet_name}!A2:C35")
          .execute()
      )
      rows = result.get("values", [])
      if rows:
        values_str = ""
        for row in rows[-1:-11:-1]:
          values_str += f"{row[0]}---{row[1]}---{row[2]}\n"
        print(values_str)
        return values_str
      else:
        print("No values here")
        return None
    except HttpError as e:
      return e, "Упс, ошибка запроса! Попробуйте повторить операцию с другой таблицей"
  except HttpError as error:
    print(f"An error occurred: {error}")
    return error
  
def delete_spreadsheet_from_sheets(user_id: int, spreadsheet_id: str):
  # Since Sheets API doesn't allow us to remove a spreadsheet directly,
  # We will use Google Drive API to remove the file from user's account.
  try:
    user = check_user_in_database(user_id)
    if user and user.access_token:
      token = json.loads(user.access_token)
      creds = Credentials.from_authorized_user_info(token, SCOPES)
      drive_service = build('drive', 'v3', credentials=creds)
      drive_service.files().delete(fileId=spreadsheet_id).execute()
      print("The spreadsheet was deleted successfully")
      return True
    else:
      print("There is no file with credentials!")
      return False
  except HttpError as error:
      print(f"An error occurred: {error}")
      return error
