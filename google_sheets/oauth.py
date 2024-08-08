# from google_auth_oauthlib.flow import InstalledAppFlow, Flow
import google_auth_oauthlib.flow
import os
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from bot_routers.utils import SharedState, user_ids
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse, RedirectResponse, HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.requests import Request
from dotenv import load_dotenv
from database.db_crud_operations import check_user_in_db
from aiogram import BaseMiddleware
from aiogram.types import Message
from database.db_crud_operations import check_user_in_db, add_user_to_db
from bot_routers.utils import SharedState, user_ids
from typing import Callable, Dict, Any, Awaitable

load_dotenv()

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
CREDENTIALS = "credentials_web.json"
SECRET_KEY = os.getenv("SECRET_KEY", None)
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
FASTAPI_HOST = "http://127.0.0.1:8000"

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)


class AuthorizationMiddleware(BaseMiddleware):
    user_telegram_id = None

    async def __call__(self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if not await self.is_user_authorized(event.from_user.id):
            # If not, redirect to Google authorization flow 
            await event.answer(
                "Для начала использования бота, пожалуйста, авторизуйтесь через свой Google аккаунт: \n\n"
                f"{FASTAPI_HOST}/authorize?telegram_user_id={event.from_user.id}"
            )
            await event.answer(f"Ваш user_id: {event.from_user.id}")

        else:
            await handler(event, data)

    async def is_user_authorized(self, user_id: int):
        # Check if the user has an associated access token 
        # Replace this with your database query or token storage mechanism
        user = await check_user_in_db(telegram_id=user_id)
        if not user:
            
            return None
        return user.access_token if user.access_token else None

@app.get('/', response_class=HTMLResponse)
async def index():
  return print_index_table()

@app.get('/test', response_class=PlainTextResponse)
def test(request: Request):
  if 'credentials' not in request.session:
    return RedirectResponse("/authorize")

  # Load credentials from the session.
  credentials = Credentials(
      **request.session['credentials'])

#   drive = googleapiclient.discovery.build(
#       API_SERVICE_NAME, API_VERSION, credentials=credentials)

#   files = drive.files().list().execute()

  # Save credentials back to session in case access token was refreshed.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
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


@app.get('/oauth2callback', response_class=RedirectResponse)
async def oauth2callback(request: Request):
  # Specify the state when creating the flow in the callback so that it can
  # verified in the authorization server response.
  state = request.session['state']
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CREDENTIALS, scopes=SCOPES, state=state)
  flow.redirect_uri = request.url_for("oauth2callback") # "http://127.0.0.1:8000/oauth2callback"
  query_params = request.query_params
  authorization_code = query_params.get('code')
  # Use the authorization server's response to fetch the OAuth 2.0 tokens.
  flow.fetch_token(code=authorization_code)
  # Store credentials in the session.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  credentials = flow.credentials
  request.session['credentials'] = credentials_to_dict(credentials)
  telegram_id = request.session["telegram_id"]
  if telegram_id:
    user = await check_user_in_db(telegram_id)
    if not user:
      user = await add_user_to_db(telegram_id=int(telegram_id))
    token_path = f"database/users_tokens/{telegram_id}.json"
    with open(f"{token_path}", "w") as token:
      token.write(credentials.to_json())
    user.access_token = token_path
    return RedirectResponse("/test")
  return PlainTextResponse("Авторизация неуспешна")

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

def print_index_table():
  return ('<table>' +
          '<tr><td><a href="/test">Проверить актуальность доступа к Google Sheets</a></td>' +
          '<td>Submit an API request and see a formatted JSON response. ' +
          '    Go through the authorization flow if there are no stored ' +
          '    credentials for the user.</td></tr>' +
          '<tr><td><a href="/authorize">Нажмите на ссылку, чтобы авторизоваться в сервисе Google</a></td>' +
          '<td>Вам будет необходимо выбрать свой Google аккаунт, ' +
          'для которого вы хотите создать Google таблицу с расходами</td></tr>' +
          '</table>')
