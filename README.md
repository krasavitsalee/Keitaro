# Keitaro Wrapper

FastAPI + SQLAlchemy обёртка над Keitaro Tracker Admin API.

## Функционал

1. **Создаватор кампаний** (`/creator`) — создаёт кампанию с двумя потоками:
   - поток 1: ловит всех из указанной страны (geo-фильтр) и редиректит на Google;
   - поток 2: редиректит на выбранный оффер.
   - У кампании настраиваются домен, группа и источник (из API Keitaro).

2. **Редактор кампаний** (`/editor`) — добавление/удаление офферов в потоках кампании.

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# заполните KEITARO_URL и KEITARO_API_KEY в .env
```

### Миграции БД

```bash
alembic upgrade head
```

(Таблицы также создаются автоматически при старте приложения.)

### Запуск сервера

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Откройте http://localhost:8000/creator и http://localhost:8000/editor.

## Переменные окружения

- `KEITARO_URL` — базовый URL трекера (без `/admin_api/v1`).
- `KEITARO_API_KEY` — ключ Admin API (Account → API keys).
- `DATABASE_URL` — URL БД SQLAlchemy (по умолчанию SQLite).

## Кампании

Называйте кампании с префиксом `test_<фамилия>_`, например `test_ivanov_campaign1`.