# Технический дизайн

## Backend

Добавить:

```text
backend/app/
├── core/
│   └── security.py
├── models/
│   └── admin_user.py
├── schemas/
│   ├── admin_user.py
│   └── auth.py
└── routers/
    └── auth.py
```

Модель `AdminUser` хранится в таблице `admin_users` и содержит `id`, уникальный `login`, `nickname`, `password_hash`, `is_active`, `created_at`, `updated_at`.

Для хеширования использовать доступный в Python стандартный `hashlib.scrypt` с солью. Пароль никогда не хранится и не возвращается в API.

JWT реализовать через `python-jose`. Секрет и срок жизни задаются через `JWT_SECRET` и `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`, значение срока по умолчанию 60 минут.

Auth API:

- `GET /api/auth/registration-status` — доступна ли публичная регистрация;
- `POST /api/auth/register` — регистрация первого администратора;
- `POST /api/auth/login` — проверка логина/пароля и выдача access-токена;
- `GET /api/auth/me` — текущий администратор по JWT;
- `POST /api/auth/admins` — создание администратора авторизованным администратором.

Dependency `get_current_admin` проверяет Bearer JWT и активность пользователя.

## Защита роутов

- `GET /api/admin-settings` публичный;
- остальные методы `admin-settings` защищены `get_current_admin`;
- `POST /api/leads` публичный;
- остальные методы `leads` защищены `get_current_admin`.

## Frontend

Добавить маршрут `/admin/` без отдельного фреймворка, используя существующий Vite frontend. На `/admin/`:

- без токена показывать форму входа;
- перед формой входа запрашивать `registration-status`;
- кнопку регистрации показывать только при `can_register = true`;
- после входа сохранять токен в `sessionStorage`;
- запрашивать услуги и выполнять CRUD через Bearer token;
- добавить форму создания/редактирования услуги;
- добавить физическое удаление услуги;
- добавить создание администраторов авторизованным администратором;
- добавить выход с удалением токена.

Основной маршрут `/` и публичная загрузка услуг не меняются.

## База данных

Таблицы создаются существующим `Base.metadata.create_all` при старте backend. Миграционная система в проекте отсутствует.

## Проверка

- `python -m compileall backend`;
- `python -m pytest backend/tests`;
- `docker compose config --quiet`;
- production frontend build;
- smoke-тест auth endpoints, JWT-защиты и публичного списка услуг через Nginx.
