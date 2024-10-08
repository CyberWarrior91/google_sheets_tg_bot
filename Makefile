start-bot:
	python3 -m bot_main

fastapi_dev:
	python3 -m fastapi dev google_sheets/oauth.py

fastapi_prod:
	python3 -m fastapi run google_sheets/oauth.py

docker-compose:
	docker compose up --build

docker-build:
	docker build -t oauth_app:latest .
