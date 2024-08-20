# from google_auth_oauthlib.flow import InstalledAppFlow, Flow
import google_auth_oauthlib.flow
import os
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse, RedirectResponse, HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.requests import Request
from dotenv import load_dotenv
from database.db_crud_operations import (
    check_user_in_db, 
    add_user_to_db,
    add_token_to_user
)
load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
CREDENTIALS = "credentials_web.json"
SECRET_KEY = os.getenv("SECRET_KEY", None)
BOT_URL = os.getenv("BOT_URL", "")
FASTAPI_HOST = os.getenv("FASTAPI_HOST", "http://127.0.0.1:8000")
DEBUG=os.getenv("DEBUG", True)
if DEBUG:
  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)


# @app.get('/', response_class=HTMLResponse)
# async def index():
#   return print_index_table()

@app.get('/test', response_class=PlainTextResponse)
def test(request: Request):
  if 'credentials' not in request.session:
    return RedirectResponse("/authorize")

  # Load credentials from the session.
  credentials = Credentials(
      **request.session['credentials'])
  request.session['credentials'] = credentials_to_dict(credentials)

  return "Ваш аккаунт авторизован! Можете вернуться в диалог с ботом"

@app.get('/authorize', response_class=RedirectResponse)
def authorize(request: Request):
  # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CREDENTIALS, scopes=SCOPES)

  # The URI created here must exactly match one of the authorized redirect URIs
  # for the OAuth 2.0 client, which you configured in the API Console. If this
  # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
  # error.
  flow.redirect_uri = request.url_for("oauth2callback")
  authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')
  # Store the state so the callback can verify the auth server response.
  telegram_user_id = request.query_params.get('telegram_user_id')
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
    user = await check_user_in_db(telegram_id)
    if not user:
      user = await add_user_to_db(telegram_id=int(telegram_id))
    token_path = f"database/users_tokens/{telegram_id}.json"
    with open(f"{token_path}", "w") as token:
      token.write(credentials.to_json())
    await add_token_to_user(telegram_id, token_path)
    return HTMLResponse(
      "<p>Авторизация прошла успешно! Для возврата в бот, нажмите на " +
      "<a href='https://t.me/dirty_little_email_parser_bot/'>кнопку</a></p>")
  return PlainTextResponse("Авторизация неуспешна")

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

# def print_index_table():
#   return ('<table>' +
#           '<tr><td><a href="/test">Проверить актуальность доступа к Google Sheets</a></td>' +
#           '<td>Submit an API request and see a formatted JSON response. ' +
#           '    Go through the authorization flow if there are no stored ' +
#           '    credentials for the user.</td></tr>' +
#           '<tr><td><a href="/authorize">Нажмите на ссылку, чтобы авторизоваться в сервисе Google</a></td>' +
#           '<td>Вам будет необходимо выбрать свой Google аккаунт, ' +
#           'для которого вы хотите создать Google таблицу с расходами</td></tr>' +
#           '</table>')
