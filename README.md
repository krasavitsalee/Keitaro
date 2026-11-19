# Keitaro Wrapper

Веб-обёртка над рекламным трекером **Keitaro** (Admin API). Позволяет создавать кампании по шаблону и редактировать офферы в существующих кампаниях.

## Стек

- **Backend:** FastAPI, SQLAlchemy, Alembic
- **Frontend:** HTML / CSS / JavaScript (без фреймворков)
- **Интеграция:** Keitaro Admin API (httpx)
- **БД:** SQLite (по умолчанию), можно заменить на PostgreSQL через `DATABASE_URL`
- **Тесты:** pytest (11 шт.)

## Функционал

### 1. Создаватор кампаний (`/creator`)
Принимает название кампании, гео-код страны и ID оффера. Создаёт кампанию с:
- настроенными доменом, группой и источником трафика (из API Keitaro);
- потоком 1: фильтр `country accept [XX]` → редирект на Google;
- потоком 2 (default): редирект на выбранный оффер.

### 2. Редактор кампаний (`/editor`)
- Список кампаний из Keitaro.
- Просмотр потоков и офферов.
- Добавление/удаление офферов.
- Распределение весов (процентов) с закреплением.
- Архив удалённых офферов с возможностью восстановления.
- Синхронизация с Keitaro (проверка ручных изменений).
- Применение изменений по кнопке (batch).

## Установка и запуск

### 1. Клонирование и зависимости

```bash
git clone <repo-url>
cd keitaro-wrapper
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Настройка окружения

```bash
cp .env.example .env
```

Заполни `.env`:

```env
KEITARO_URL=https://your-tracker.example.com
KEITARO_API_KEY=your-api-key
DATABASE_URL=sqlite:///./keitaro_wrapper.db
```

- `KEITARO_URL` — адрес трекера без `/admin_api/v1`.
- `KEITARO_API_KEY` — ключ из Keitaro: **Account → API keys**.

### 3. Миграции БД

```bash
alembic upgrade head
```

Таблицы также создаются автоматически при старте приложения.

### 4. Запуск сервера

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Или:

```bash
chmod +x run.sh && ./run.sh
```

Открой в браузере:
- Главная: http://localhost:8000/
- Создаватор: http://localhost:8000/creator
- Редактор: http://localhost:8000/editor

## API-эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/` | Главная страница |
| GET | `/creator` | Страница создаватора |
| GET | `/editor` | Страница редактора |
| GET | `/api/keitaro/domains` | Список доменов из Keitaro |
| GET | `/api/keitaro/groups` | Список групп |
| GET | `/api/keitaro/sources` | Список источников трафика |
| GET | `/api/keitaro/offers` | Список офферов |
| POST | `/api/creator/create` | Создать кампанию |
| GET | `/api/editor/campaigns` | Список кампаний |
| GET | `/api/editor/campaigns/{id}/streams` | Потоки кампании |
| GET | `/api/editor/offers` | Список офферов |
| GET | `/api/editor/streams/{id}` | Детали потока |
| POST | `/api/editor/streams/{id}/offers/add` | Добавить оффер |
| POST | `/api/editor/streams/{id}/offers/remove` | Удалить оффер |
| POST | `/api/editor/streams/{id}/offers/apply` | Применить изменения (веса) |

## Тесты

```bash
pytest
```

11 тестов, все проходят без предупреждений.

## Миграции

Создание новой миграции после изменения моделей:

```bash
alembic revision --autogenerate -m "описание"
alembic upgrade head
```

Откат:

```bash
alembic downgrade -1
```

## Нейминг кампаний

Называй кампании с префиксом `test_<фамилия>_`, например `test_ivanov_campaign1`. Приложение не принуждает к префиксу — это ответственность пользователя.

## Структура проекта

```
keitaro-wrapper/
├── app/
│   ├── main.py              # FastAPI app, маршруты
│   ├── config.py            # Настройки из .env
│   ├── database.py          # SQLAlchemy engine/session
│   ├── models/db.py         # Модели CampaignRecord, OfferChangeLog
│   ├── services/keitaro.py  # Клиент Keitaro Admin API
│   ├── routers/
│   │   ├── creator.py       # Создаватор кампаний
│   │   └── editor.py        # Редактор кампаний
│   ├── templates/           # HTML-страницы
│   └── static/style.css     # Стили
├── migrations/              # Alembic-миграции
├── tests/                   # pytest-тесты (11 шт.)
├── requirements.txt
├── .env.example
├── alembic.ini
├── run.sh
└── README.md
```