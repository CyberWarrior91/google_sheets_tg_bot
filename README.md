## Начало работы

**Описание:**

Expense Revisor Bot - телеграм бот, интегрированный с сервисом Google Sheets, который позволит вам создать и вести таблицы по ежедневным расходам. Бот доступен по этой <a href="https://t.me/ExpenseRevisorBot">ссылке</a>

## Использование

Для локального запуска бота, пройдите следующие шаги:

#### Склонируйте репозиторий по этой команде:
```git clone https://github.com/CyberWarrior91/google_sheets_tg_bot.git```

**Требования:**
 
В приложении используются следующие зависимости:
 
aiofiles==23.2.1

aiogram==3.10.0

aiohappyeyeballs==2.3.4

aiohttp==3.9.0

aiosignal==1.3.1

annotated-types==0.7.0

anyio==4.4.0

async-timeout==4.0.3

asyncpg==0.29.0
attrs==23.2.0
cachetools==5.4.0
certifi==2024.7.4
charset-normalizer==3.3.2
click==8.1.7
dnspython==2.6.1
email_validator==2.2.0
exceptiongroup==1.2.2
fastapi==0.112.0
fastapi-cli==0.0.5
frozenlist==1.4.1
google-api-core==2.19.1
google-api-python-client==2.137.0
google-auth==2.32.0
google-auth-httplib2==0.2.0
google-auth-oauthlib==1.2.1
googleapis-common-protos==1.63.2
greenlet==3.0.3
h11==0.14.0
httpcore==1.0.5
httplib2==0.22.0
httptools==0.6.1
httpx==0.27.0
idna==3.7
itsdangerous==2.2.0
Jinja2==3.1.4
magic-filter==1.0.12
markdown-it-py==3.0.0
MarkupSafe==2.1.5
mdurl==0.1.2
multidict==6.0.5
oauthlib==3.2.2
proto-plus==1.24.0
protobuf==5.27.2
psycopg2-binary==2.9.9
pyasn1==0.6.0
pyasn1_modules==0.4.0
pydantic==2.8.2
pydantic_core==2.20.1
Pygments==2.18.0
pyparsing==3.1.2
python-dotenv==1.0.1
python-multipart==0.0.9
python-socks==2.5.0
pytz==2024.2
PyYAML==6.0.1
requests==2.32.3
requests-oauthlib==2.0.0
rich==13.7.1
rsa==4.9
shellingham==1.5.4
sniffio==1.3.1
SQLAlchemy==2.0.31
starlette==0.37.2
typer==0.12.3
typing_extensions==4.12.2
uritemplate==4.1.1
urllib3==2.2.2
uvicorn==0.30.5
uvloop==0.19.0
watchfiles==0.22.0
websockets==12.0
yarl==1.9.4

Основные библиотеки: google-api-python-client, google-auth-httplib2, google-auth-oauthlib (для обращения к методам Google Sheets по API), FastAPI (создание сервера для прохождения авторизации для Google) и aiogram (для манипуляций с Telegram ботом)

Установите их следующими командами:

```python -m pip --version```

```python -m pip install --upgrade pip```

```python -m pip install -r requirements.txt```

Также вам будет необходимо определить следующие переменные окружения в файле .env:

BOT_TOKEN (токен вашего бота, который выдает <a href="https://t.me/BotFather">BotFather</a>)
BOT_URL (ссылка на ваш Telegram бот)
SECRET_KEY (секретный ключ для инициализации приложения FastAPI)
DATABASE_URL (ссылка на соединение с базой данных PostgreSQL)

## Makefile

Для запуска приложения возможно использование следующих команд из файла Makefile

### Makefile commands:

```start-bot``` запустить локально Telegram бот

```fastapi_dev``` запустить приложение FastAPI в тестовой среде

```fastapi_prod``` запустить приложение FastAPI в продакшн среде

```docker-build``` создать Docker образ для приложения FastAPI

```docker-compose``` запустить контейнер в Docker Compose со следующими процессами: Telegram бот, приложение FastAPI, база данных PostgreSQL
