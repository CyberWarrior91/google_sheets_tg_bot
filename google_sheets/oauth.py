# from google_auth_oauthlib.flow import InstalledAppFlow, Flow
import google_auth_oauthlib.flow
import os
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse, RedirectResponse, HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.requests import Request
import json
from dotenv import load_dotenv
from database.db_crud_operations import (
    check_user_in_database, 
    add_user_to_db,
    add_token_to_user,
    remove_token_from_user_in_db
)
import requests
load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
CREDENTIALS = "credentials_web.json"
SECRET_KEY = os.getenv("SECRET_KEY", None)
BOT_URL = os.getenv("BOT_URL", "")
FASTAPI_HOST = os.getenv("FASTAPI_HOST", "http://127.0.0.1:8000")
DEBUG=os.getenv("DEBUG", True)
if DEBUG is True:
  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)


@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
  telegram_id = request.query_params.get('telegram_id')
  return print_index_table(telegram_id)

@app.get('/main', response_class=PlainTextResponse)
def test(request: Request):
  if 'credentials' not in request.session:
    
    return RedirectResponse("/authorize")
  # Load credentials from the session.
  credentials = Credentials(
      **request.session['credentials'])
  request.session['credentials'] = credentials_to_dict(credentials)
  return PlainTextResponse(f"Creds: {request.session.get('credentials')}")
  return "Ваш аккаунт уже авторизован! Можете вернуться в диалог с ботом"

@app.get('/authorize', response_class=RedirectResponse)
def authorize(request: Request):
  # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CREDENTIALS, scopes=SCOPES)
  flow.redirect_uri = request.url_for("oauth2callback")
  authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')
  # Store the state so the callback can verify the auth server response.
  telegram_user_id = request.query_params.get('telegram_id')
  request.session['telegram_id'] = telegram_user_id
  request.session['state'] = state
  return authorization_url


@app.get('/oauth2callback')
async def oauth2callback(request: Request):
  # Specify the state when creating the flow in the callback so that it can
  # verified in the authorization server response.
  state = request.session['state']
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CREDENTIALS, scopes=SCOPES, state=state)
  flow.redirect_uri = request.url_for("oauth2callback")
  query_params = request.query_params
  authorization_code = query_params.get('code')
  # Use the authorization server's response to fetch the OAuth 2.0 tokens.
  flow.fetch_token(code=authorization_code)
  # Store credentials in the session.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  credentials = flow.credentials
  request.session['credentials'] = credentials_to_dict(credentials)
  telegram_id = int(request.session["telegram_id"])
  if telegram_id:
    user = check_user_in_database(telegram_id)
    if not user:
      user = add_user_to_db(telegram_id=int(telegram_id))
    creds_string = json.dumps(request.session["credentials"])
    add_token_to_user(telegram_id=telegram_id, token=creds_string)
    revoke_url = f'{request.url_for("revoke")}?telegram_id={telegram_id}'
    return HTMLResponse(
    f"<p>Авторизация прошла успешно! Для возврата в бот, нажмите на " +
    f"<a href='{BOT_URL}'>кнопку</a> или закройте данное окно в браузере"
    "<br>"
    f"Чтобы отозвать доступ к своему Google аккаунту, нажмите <a href='{revoke_url}'>здесь</a></p>")
  return PlainTextResponse("Авторизация неуспешна")

@app.get('/revoke')
def revoke(request: Request, telegram_id: int | None = None):
  if 'credentials' not in request.session:
    return HTMLResponse('Вам необходимо <a href="/authorize">авторизоваться </a> перед ' +
            'тем, как отзывать доступ к своему Google аккаунту')

  credentials = Credentials(**request.session['credentials'])

  revoke = requests.post('https://oauth2.googleapis.com/revoke',
      params={'token': credentials.token},
      headers = {'content-type': 'application/x-www-form-urlencoded'})

  status_code = getattr(revoke, 'status_code')
  if status_code == 200:
    telegram_id = request.query_params.get("telegram_id")
    result = remove_token_from_user_in_db(telegram_id)
    if result:
      return PlainTextResponse('Доступ успешно отозван.')
    return PlainTextResponse("Ошибка удаления токена")
  else:
    return PlainTextResponse('Доступ уже был отозван либо вы не авторизованы в сервисе Google')
  
def credentials_to_dict(credentials: Credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

def print_index_table(telegram_id):
  return ('<table>' +
          f'<tr><td><a href="/authorize?telegram_id={telegram_id}">Авторизоваться в сервисе Google</a></td>' +
          '<td>Вам будет необходимо выбрать свой Google аккаунт, ' +
          'для которого вы хотите создать Google таблицу с расходами</td></tr>' +
          f'<tr><td><a href="/revoke?telegram_id={telegram_id}">Отозвать доступ к своему Google аккаунту</a></td>' +
          '<td>Нажмите на ссылку, чтобы больше не предоставлять доступ к своему Google аккаунту для сервисов ' +
          'Google или выбрать другой аккаунт для использования сервиса Google Spreadsheets</td></tr>'
          '</table>')
