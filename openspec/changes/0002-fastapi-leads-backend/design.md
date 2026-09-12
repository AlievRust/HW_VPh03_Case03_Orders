# Технический дизайн

## Структура

```text
backend/
├── app/
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   ├── models/
│   │   ├── base.py
│   │   ├── lead.py
│   │   ├── analytics.py
│   │   └── admin_settings.py
│   ├── routers/
│   │   ├── leads.py
│   │   ├── analytics.py
│   │   └── admin_settings.py
│   ├── schemas/
│   │   ├── lead.py
│   │   ├── analytics.py
│   │   └── admin_settings.py
│   └── main.py
├── Dockerfile
└── requirements.txt
```

## Технологии

- Python 3.12.
- FastAPI.
- Uvicorn.
- SQLAlchemy 2.x.
- psycopg 3 binary driver.
- PostgreSQL JSONB для списка аналитических событий.
- `Base.metadata.create_all` при старте приложения.

## Подключение к БД

Backend использует переменные Compose:

- `POSTGRES_DB`;
- `POSTGRES_USER`;
- `POSTGRES_PASSWORD`;
- host `postgres`;
- port `5432`.

Строка подключения формируется в `core/database.py`. Engine и session dependency не должны использовать внешнее подключение к PostgreSQL.

## Модель `Lead`

Таблица: `leads`.

Поля:

- `id` — integer primary key;
- `first_name`, `last_name`, `middle_name` — контактное имя;
- `contact_value` — телефон, email или иной контакт;
- `business_niche` — ниша бизнеса;
- `company_size` — размер компании;
- `business_info` — дополнительная информация о бизнесе;
- `task_volume` — объём потребности;
- `budget` — бюджет строкой;
- `result_deadline` — срок результата;
- `customer_role` — сотрудник или руководитель;
- `task_type` — тип задачи;
- `product_interest` — интересующий продукт;
- `contact_method` — предпочтительный способ связи;
- `preferred_time` — удобное время;
- `comments` — комментарий;
- `created_at`, `updated_at` — UTC-время.

SQL для таблицы указывается в docstring класса модели.

## Модель `LeadAnalytics`

Таблица: `lead_analytics`.

Поля:

- `lead_id` — integer primary key и foreign key на `leads.id` с cascade delete;
- `time_on_page_seconds` — время на странице;
- `button_clicks` — число нажатий;
- `cursor_pauses` — число задержек курсора;
- `return_visits` — число возвратов;
- `events` — JSONB-массив технических и поведенческих событий;
- `technical_info` — JSONB-техническая информация;
- `created_at`, `updated_at` — UTC-время.

Связь с `Lead` — один-к-одному.

## Модель `AdminSettings`

Таблица: `admin_settings`.

Поля:

- `id` — integer primary key;
- `service_name` — название услуги;
- `service_description` — описание;
- `budget_min` — нижняя граница бюджета;
- `budget_max` — верхняя граница бюджета;
- `budget_step` — шаг ползунка;
- `is_active` — признак активности;
- `created_at`, `updated_at` — UTC-время.

SQL для таблицы указывается в docstring класса модели.

## API

Общий prefix: `/api`.

### Leads

- `POST /api/leads` — создать заявку с вложенными analytics и вернуть созданную заявку;
- `GET /api/leads/{lead_id}` — получить заявку;
- `GET /api/leads` — получить список заявок с `skip` и `limit`;
- `PUT /api/leads/{lead_id}` — полностью обновить заявку;
- `DELETE /api/leads/{lead_id}` — удалить заявку.

### Analytics

- `POST /api/analytics` — создать или заменить аналитику заявки;
- `GET /api/analytics/{lead_id}` — получить аналитику;
- `PUT /api/analytics/{lead_id}` — обновить аналитику;
- `DELETE /api/analytics/{lead_id}` — удалить аналитику.

### Admin settings

- `POST /api/admin-settings`;
- `GET /api/admin-settings`;
- `GET /api/admin-settings/{setting_id}`;
- `PUT /api/admin-settings/{setting_id}`;
- `DELETE /api/admin-settings/{setting_id}`.

Служебные endpoints:

- `GET /api/health` — проверка доступности приложения без обращения к БД через Nginx;
- `GET /api/health/db` — проверка соединения с PostgreSQL через Nginx.

Внутренние варианты `/health` и `/health/db` также оставлены для прямых запросов внутри Docker-сети.

## Приватность Compose

Backend подключается только к `private` network и не получает секцию `ports`. Nginx подключён к `private` и проксирует `/api/` на `http://backend:8000/`. PostgreSQL остаётся без host-порта.

## Проверка

- `docker compose config --quiet`;
- `python -m compileall backend`;
- pytest для моделей, CRUD и API;
- проверка `docker compose ps` и отсутствия host-порта у backend;
- проверка `GET /api/health` через Nginx.
