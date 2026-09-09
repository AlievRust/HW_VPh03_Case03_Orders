# Проектирование: Docker-инфраструктура

## Сервисы

| Сервис | Назначение | Внешний доступ |
| --- | --- | --- |
| `nginx` | Раздача frontend и проксирование запросов к будущему backend и pgAdmin | Порт `NGINX_PORT` |
| `postgres` | Локальное хранилище данных backend | Нет |
| `pgadmin` | Администрирование PostgreSQL через браузер | Только через Nginx по пути `/pgadmin/` |
| `registry` | Приватное хранилище образов backend | Порт `REGISTRY_PORT` |
| `watchtower` | Обновление контейнеров, отмеченных меткой | Нет |
| `backend` | Будущий сервис API | Оставлен закомментированным |

## Сети

- `public`: Nginx и Registry; к Nginx подключаются pgAdmin и будущий backend для проксирования.
- `private`: помечена как `internal: true`; содержит PostgreSQL, pgAdmin и будущий backend.
- PostgreSQL не имеет опубликованных портов и не подключён к публичной сети.

## Переменные окружения

В `.env.example` должны быть перечислены:

- `NGINX_PORT`;
- `REGISTRY_PORT`;
- `POSTGRES_DB`;
- `POSTGRES_USER`;
- `POSTGRES_PASSWORD`;
- `PGADMIN_DEFAULT_EMAIL`;
- `PGADMIN_DEFAULT_PASSWORD`.

Секреты задаются только в локальном `.env`, исключённом из Git.

## Registry

Registry использует образ `registry:2`, volume для образов и bind mount файла `registry/auth/htpasswd`.

- Сервис публикует `REGISTRY_PORT:5000` на всех сетевых интерфейсах хоста.
- Аутентификация включается переменными `REGISTRY_AUTH=htpasswd` и `REGISTRY_AUTH_HTPASSWD_REALM`.
- Файл создаётся администратором командой с контейнером `httpd:2` и не хранится в репозитории.
- Registry работает по HTTP в учебной локальной сети. Docker-клиенту требуется настройка `insecure-registries` для адреса `IP_СЕРВЕРА:REGISTRY_PORT`.

## Nginx

Nginx использует конфигурацию `nginx/default.conf`:

- `/` отдаёт статические файлы из `/usr/share/nginx/html`.
- `/pgadmin/` проксируется на `pgadmin:80` с настройками для работы за обратным прокси.
- Блок `/api/` для будущего backend оставляется закомментированным.

## Watchtower

Watchtower получает доступ к Docker socket и запускается с `--label-enable`. Контейнеры обновляются только при наличии метки `com.centurylinklabs.watchtower.enable=true`; на старте ни один сервис её не получает.

## Персистентность

- `postgres_data`: данные PostgreSQL.
- `registry_data`: образы Registry.
- `pgadmin_data`: настройки pgAdmin.

## Ограничения

- Compose не может самостоятельно установить Docker Engine или Docker Compose: их устанавливают на хосте заранее.
- HTTP Registry не защищает передаваемые пароли. Переход на реальное окружение требует TLS и безопасного управления учётными данными.
