## Начало работы

**Описание:**

Expense Revisor Bot - телеграм бот, интегрированный с сервисом Google Sheets, который позволит вам создать и вести таблицы по ежедневным расходам. Бот доступен по этой <a href="https://t.me/ExpenseRevisorBot">ссылке</a>

## Использование

Для локального запуска бота, пройдите следующие шаги:

#### Склонируйте репозиторий по этой команде:
```git clone https://github.com/CyberWarrior91/google_sheets_tg_bot.git```

**Требования:**
 
В приложении используются следующие зависимости:
 
```aiogram==3.10.0

aiohttp==3.9.0```

fastapi==0.112.0

fastapi-cli==0.0.5

google-api-core==2.19.1

google-api-python-client==2.137.0

google-auth==2.32.0

google-auth-httplib2==0.2.0

google-auth-oauthlib==1.2.1

googleapis-common-protos==1.63.2

oauthlib==3.2.2

psycopg2-binary==2.9.9

pydantic==2.8.2

pydantic_core==2.20.1

pytz==2024.2

PyYAML==6.0.1

requests==2.32.3

requests-oauthlib==2.0.0

SQLAlchemy==2.0.31

starlette==0.37.2

urllib3==2.2.2

uvicorn==0.30.5

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
