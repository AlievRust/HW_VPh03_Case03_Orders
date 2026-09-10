# Orders: учебная Docker-инфраструктура

Учебный проект для сбора заявок от «тёплых клиентов». На текущем этапе в репозитории подготовлена контейнерная инфраструктура: обратный прокси Nginx, PostgreSQL, pgAdmin, локальный Docker Registry и Watchtower.

Backend пока не реализован и не запускается. Его пример оставлен в `docker-compose.yml` в виде закомментированного блока.

## Содержание

- [Архитектура](#архитектура)
- [Что нужно установить](#что-нужно-установить)
- [Структура проекта](#структура-проекта)
- [Первоначальная настройка](#первоначальная-настройка)
- [Запуск](#запуск)
- [Доступ к сервисам](#доступ-к-сервисам)
- [Работа с Docker Registry](#работа-с-docker-registry)
- [Проверка](#проверка)
- [Остановка и удаление данных](#остановка-и-удаление-данных)
- [Watchtower](#watchtower)
- [Безопасность учебного решения](#безопасность-учебного-решения)
- [Типовые проблемы](#типовые-проблемы)

## Архитектура

Все сервисы запускаются через Docker Compose.

```text
Клиент в локальной сети
        |
        | HTTP : NGINX_PORT
        v
     Nginx
      |  \
      |   \-- /pgadmin/ --> pgAdmin --> PostgreSQL
      |
      \-- /api/ ---------> будущий backend

Docker-клиент в локальной сети
        |
        | HTTP : REGISTRY_PORT + docker login
        v
    Docker Registry
```

### Сервисы

| Сервис | Назначение | Доступ с хоста |
| --- | --- | --- |
| `nginx` | Раздаёт frontend и проксирует pgAdmin и будущий API | `NGINX_PORT` |
| `postgres` | Хранит данные приложения | Не публикует порт |
| `pgadmin` | Веб-интерфейс PostgreSQL | Через Nginx: `/pgadmin/` |
| `registry` | Хранит Docker-образы будущего backend | `REGISTRY_PORT` |
| `watchtower` | Обновляет контейнеры с соответствующей меткой | Не публикует порт |
| `backend` | Будущий API | Пока отключён комментарием |

### Сети

- `orders_public` используется Nginx и Registry.
- `orders_private` помечена как `internal: true` и используется PostgreSQL, pgAdmin и будущим backend.
- PostgreSQL не имеет проброса порта на хост, поэтому внешние клиенты не могут подключиться к нему напрямую.
- Nginx подключён к обеим сетям, чтобы принимать внешние HTTP-запросы и обращаться к внутренним сервисам.

### Постоянное хранение

Docker volumes сохраняют данные после пересоздания контейнеров:

- `postgres_data` — база PostgreSQL;
- `pgadmin_data` — настройки pgAdmin;
- `registry_data` — загруженные Docker-образы.

## Что нужно установить

На машине, где запускается инфраструктура, установите:

- Docker Desktop для Windows/macOS или Docker Engine для Linux;
- Docker Compose Plugin с командой `docker compose`;
- Docker CLI на машинах, с которых выполняется push образов.

Проверка установки:

```powershell
docker --version
docker compose version
```

Compose-файл не устанавливает Docker автоматически. Установка Docker выполняется отдельно на хостовой машине.

### Оболочка команд

Примеры в README приведены для Windows PowerShell. На Linux-VPS используйте эквиваленты:

| Windows PowerShell | Linux/macOS (bash) |
| --- | --- |
| `Copy-Item .env.example .env` | `cp .env.example .env` |
| `\| Out-File -Encoding ascii файл` | `> файл` |
| `Test-Path файл` | `test -f файл && echo ok` |
| `Invoke-WebRequest URL -SkipHttpErrorCheck` | `curl -i URL` |
| `"${PWD}\путь"` | `"$(pwd)/путь"` |

Команды `docker`, `docker compose`, `docker login`, `docker tag`, `docker push` и `docker pull` одинаковы в обеих оболочках.

## Структура проекта

```text
.
├── .env.example                         # шаблон переменных окружения
├── .gitignore                           # исключения секретов и локальных данных
├── docker-compose.yml                   # описание контейнеров и сетей
├── frontend/
│   └── index.html                       # стартовая страница до подключения приложения
├── nginx/
│   └── default.conf                     # маршруты Nginx
├── registry/
│   └── auth/
│       └── .gitkeep                     # фиксация каталога в Git
├── docs/
│   ├── changelog.md                     # история изменений
│   └── technical_overview.md            # техническая документация
└── openspec/                             # спецификации изменений
```

Git не отслеживает пустые каталоги, поэтому `frontend/` и `registry/auth/` зафиксированы файлами `index.html` и `.gitkeep`. Оба каталога появятся после `git clone` или `git pull` на сервере, создавать их вручную не нужно.

## Первоначальная настройка

### 1. Создать локальный `.env`

Скопируйте шаблон:

```bash
cp .env.example .env
```

```powershell
Copy-Item .env.example .env
```

Откройте `.env` и замените:

- `REGISTRY_HOST` — IP-адрес машины, на которой работает Registry;
- `POSTGRES_PASSWORD` — пароль PostgreSQL;
- `PGADMIN_DEFAULT_PASSWORD` — пароль pgAdmin;
- `NGINX_PORT` и `REGISTRY_PORT` — при необходимости, если стандартные порты заняты.

Файл `.env` исключён из Git и не должен публиковаться.

### 2. Разместить frontend

Каталог `frontend/` уже есть в репозитории и содержит учебную страницу `index.html`, поэтому после `git pull` на сервере он доступен сразу. Когда приложение будет готово, замените эту страницу файлами собранного frontend. Nginx всегда ищет стартовый файл `index.html`.

### 3. Создать пользователя Registry

Каталог `registry/auth/` тоже зафиксирован в репозитории файлом `.gitkeep`. На сервере остаётся создать только один файл — `htpasswd` с хешем пароля.

Linux/macOS (bash):

```bash
docker run --rm --entrypoint htpasswd httpd:2 -Bbn registry-user 'CHANGE_THIS_PASSWORD' > registry/auth/htpasswd
```

Безопасный вариант для bash — пароль не попадёт в историю команд:

```bash
read -s REGISTRY_PASSWORD
docker run --rm --entrypoint htpasswd httpd:2 -Bbn registry-user "$REGISTRY_PASSWORD" > registry/auth/htpasswd
unset REGISTRY_PASSWORD
```

Windows PowerShell:

```powershell
docker run --rm --entrypoint htpasswd httpd:2 -Bbn registry-user 'CHANGE_THIS_PASSWORD' | Out-File -Encoding ascii registry/auth/htpasswd
```

В PowerShell редирект `>` перекодирует вывод в UTF-16, и Registry не сможет прочитать такой файл, поэтому там обязателен `Out-File -Encoding ascii`. В bash, наоборот, `Out-File` не существует — используется обычный `>`.

Замените `registry-user` и `CHANGE_THIS_PASSWORD` на собственные значения. Не используйте простые пароли: Registry доступен по HTTP из локальной сети. Файл не содержит открытый пароль, но всё равно является секретом и исключён из Git.

Проверьте, что файл создан и содержит хеш bcrypt (`$2y$` в начале строки):

```bash
head -c 10 registry/auth/htpasswd; echo
```

## Запуск

Проверьте итоговую конфигурацию перед запуском:

```powershell
docker compose config
```

Запустите контейнеры в фоновом режиме:

```powershell
docker compose up -d
```

Проверьте состояние:

```powershell
docker compose ps
```

Посмотрите логи отдельного сервиса:

```powershell
docker compose logs -f nginx
docker compose logs -f postgres
docker compose logs -f pgadmin
docker compose logs -f registry
docker compose logs -f watchtower
```

## Доступ к сервисам

### Nginx и frontend

```text
http://IP_СЕРВЕРА:NGINX_PORT/
```

Если используется порт `80`, адрес будет таким:

```text
http://IP_СЕРВЕРА/
```

### pgAdmin

pgAdmin доступен через Nginx:

```text
http://IP_СЕРВЕРА:NGINX_PORT/pgadmin/
```

Для входа используйте:

- email из `PGADMIN_DEFAULT_EMAIL`;
- пароль из `PGADMIN_DEFAULT_PASSWORD`.

При добавлении сервера PostgreSQL в pgAdmin используйте следующие параметры:

| Поле | Значение |
| --- | --- |
| Host name/address | `postgres` |
| Port | `5432` |
| Maintenance database | значение `POSTGRES_DB` |
| Username | значение `POSTGRES_USER` |
| Password | значение `POSTGRES_PASSWORD` |

Имя `postgres` работает внутри Docker-сети и не является адресом для внешнего клиента.

### PostgreSQL

Порт PostgreSQL намеренно не публикуется на хост. Подключение выполняется только из контейнеров сети `orders_private`, например из pgAdmin или будущего backend.

## Работа с Docker Registry

Registry доступен по адресу:

```text
http://REGISTRY_HOST:REGISTRY_PORT
```

Например:

```text
http://192.168.1.10:5000
```

В этой учебной конфигурации Registry работает по HTTP без TLS.

### Настроить Docker-клиент

На каждой машине, с которой будет выполняться `docker push`, добавьте адрес Registry в `insecure-registries`.

В Docker Desktop:

1. Откройте **Settings → Docker Engine**.
2. Добавьте адрес Registry в JSON-конфигурацию.
3. Нажмите **Apply & Restart**.

Пример:

```json
{
  "insecure-registries": ["192.168.1.10:5000"]
}
```

На Linux добавьте аналогичную настройку в конфигурацию Docker daemon, обычно `/etc/docker/daemon.json`, затем перезапустите Docker:

```json
{
  "insecure-registries": ["192.168.1.10:5000"]
}
```

После изменения настройки проверьте вход:

```powershell
docker login 192.168.1.10:5000
```

Введите пользователя и пароль, которые использовались при создании `registry/auth/htpasswd`.

### Push и pull образа

Пример с образом Alpine:

```powershell
docker pull alpine:3.20
docker tag alpine:3.20 192.168.1.10:5000/orders-backend:test
docker push 192.168.1.10:5000/orders-backend:test
docker pull 192.168.1.10:5000/orders-backend:test
```

Для будущего backend схема будет такой:

```powershell
docker build -t 192.168.1.10:5000/orders-backend:latest .
docker push 192.168.1.10:5000/orders-backend:latest
```

### Проверить API Registry

Без авторизации Registry должен вернуть `401 Unauthorized`:

```bash
curl -i http://192.168.1.10:5000/v2/
```

```powershell
Invoke-WebRequest http://192.168.1.10:5000/v2/ -SkipHttpErrorCheck
```

Подставьте адрес вашего сервера. После успешного `docker login` команды push и pull должны выполняться без ошибки авторизации.

## Проверка

Проверка синтаксиса Compose без запуска контейнеров:

```powershell
docker compose config --quiet
```

Проверка состояния контейнеров:

```powershell
docker compose ps
```

Проверка HTTP Registry:

```bash
curl -i http://192.168.1.10:5000/v2/
```

```powershell
Invoke-WebRequest http://192.168.1.10:5000/v2/ -SkipHttpErrorCheck
```

Проверка frontend выполняется открытием адреса Nginx в браузере.

Проверка pgAdmin выполняется открытием `/pgadmin/` и авторизацией через значения из `.env`.

## Остановка и удаление данных

Остановить и удалить контейнеры, сохранив volumes:

```powershell
docker compose down
```

Запустить снова:

```powershell
docker compose up -d
```

Удалить контейнеры и volumes вместе с данными PostgreSQL, pgAdmin и Registry:

```powershell
docker compose down -v
```

Команда `docker compose down -v` необратимо удаляет локальные данные сервисов. Используйте её только для очистки учебного окружения.

## Watchtower

Watchtower запускается с параметрами:

- `--label-enable` — обновляет только контейнеры с разрешающей меткой;
- `--cleanup` — удаляет старые образы после обновления;
- `--interval 300` — проверяет обновления каждые 300 секунд.

В Compose используется образ `containrrr/watchtower:latest` и переменная `DOCKER_API_VERSION=1.40`. Это важно для совместимости с современным Docker daemon: старые версии Watchtower могут использовать Docker API ниже минимально поддерживаемой версии и завершаться ошибкой `client version 1.25 is too old`.

После изменения версии обновите только Watchtower:

```bash
docker compose pull watchtower
docker compose up -d --force-recreate watchtower
```

Проверьте логи:

```bash
docker compose logs -f watchtower
```

В Compose-примере метка включения добавлена только в закомментированный блок будущего backend:

```yaml
labels:
  com.centurylinklabs.watchtower.enable: "true"
```

Поэтому текущие инфраструктурные сервисы Watchtower автоматически не обновляет.

## Безопасность учебного решения

- Данные PostgreSQL хранятся локально в Docker volume.
- PostgreSQL не доступен напрямую с хоста.
- Backend должен получать доступ к базе только через внутреннюю Docker-сеть.
- Registry защищён логином и паролем через `htpasswd`.
- HTTP Registry не шифрует трафик. Пароль `docker login` может быть перехвачен в сети.
- HTTP Registry нельзя публиковать в интернет.
- Для production необходимо использовать TLS, безопасные секреты, ограничение сетевого доступа и регулярное резервное копирование.
- Registry публикуется на всех интерфейсах хоста (`0.0.0.0`). Если сервер имеет публичный IP-адрес, порт `REGISTRY_PORT` доступен из интернета по HTTP: закройте его файрволом (например, `ufw allow from <ваш_ip> to any port 5000`) или ограничьте публикацию адресом `127.0.0.1` в `docker-compose.yml`.
- Пароль Registry должен быть стойким: при HTTP-доступе его перебор не ограничен TLS-защитой и блокировками.
- Watchtower получает доступ к Docker socket, поэтому имеет высокий уровень привилегий на Docker-хосте.

## Типовые проблемы

### `docker compose config` сообщает о пустых переменных

Создайте `.env` из `.env.example` и заполните обязательные значения:

```bash
cp .env.example .env
```

```powershell
Copy-Item .env.example .env
```

### Registry отвечает `connection refused`

Проверьте:

```powershell
docker compose ps registry
docker compose logs registry
```

Также проверьте, что порт из `REGISTRY_PORT` свободен и доступен в локальной сети.

### Registry сразу перезапускается после `git pull`

Каталог `registry/auth` попадает в репозиторий пустым (в Git лежит только `.gitkeep`), поэтому после первой загрузки на сервере файла `htpasswd` ещё нет, и Registry не может включить авторизацию. Создайте файл и пересоздайте контейнер:

```bash
docker run --rm --entrypoint htpasswd httpd:2 -Bbn registry-user 'CHANGE_THIS_PASSWORD' > registry/auth/htpasswd
docker compose up -d --force-recreate registry
```

### `Out-File: command not found` и `write /dev/stdout: broken pipe`

Значит, команду из PowerShell-примера выполнили в bash на Linux. `Out-File` — cmdlet PowerShell, в bash его нет: оболочка не нашла команду и закрыла pipe, из-за чего `docker run` получил `broken pipe`. Сам контейнер `htpasswd` отработал корректно. Используйте редирект `>`:

```bash
docker run --rm --entrypoint htpasswd httpd:2 -Bbn registry-user 'CHANGE_THIS_PASSWORD' > registry/auth/htpasswd
```

### Docker сообщает о небезопасном Registry

Добавьте точный адрес `IP:PORT` в `insecure-registries` Docker Engine и перезапустите Docker Desktop или daemon.

### Registry отвечает `401 Unauthorized`

Это ожидаемо до авторизации. Выполните:

```powershell
docker login IP_СЕРВЕРА:REGISTRY_PORT
```

Если ошибка остаётся после входа, проверьте существование файла:

```bash
test -f registry/auth/htpasswd && echo ok
```

```powershell
Test-Path registry/auth/htpasswd
```

### pgAdmin не открывается по `/pgadmin/`

Проверьте логи Nginx и pgAdmin:

```powershell
docker compose logs nginx pgadmin
```

Адрес должен заканчиваться слешем: `/pgadmin/`.

### Порт уже занят

Измените `NGINX_PORT` или `REGISTRY_PORT` в `.env`, затем пересоздайте контейнеры:

```powershell
docker compose up -d --force-recreate
```
