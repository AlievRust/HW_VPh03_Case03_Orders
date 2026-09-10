# Технический обзор

## Docker-инфраструктура

Учебная инфраструктура запускается через Docker Compose и включает:

- `nginx` для раздачи frontend и доступа к pgAdmin;
- `postgres` для хранения данных приложения во внутренней сети Docker;
- `pgadmin` для администрирования PostgreSQL через Nginx;
- `registry` для хранения образов будущего backend;
- `watchtower` для обновления контейнеров, явно отмеченных меткой Watchtower.

PostgreSQL не публикует порт на хост и доступен только контейнерам сети `orders_private`. pgAdmin не имеет собственного опубликованного порта: он открывается через Nginx по адресу `http://IP_СЕРВЕРА:NGINX_PORT/pgadmin/`.

## Подготовка

На хосте должны быть установлены Docker Engine и Docker Compose Plugin. Создайте локальный файл настроек из шаблона:

```powershell
Copy-Item .env.example .env
```

В `.env` замените демонстрационные пароли и установите фактический IP-адрес сервера в `REGISTRY_HOST`.

Создайте файл аутентификации Registry. Команда запросит пароль пользователя Registry и сохранит только его хеш:

```powershell
docker run --rm --entrypoint htpasswd httpd:2 -Bbn registry-user 'CHANGE_THIS_PASSWORD' | Out-File -Encoding ascii registry/auth/htpasswd
```

Каталог `registry/auth` зафиксирован в Git файлом `.gitkeep`, поэтому после клонирования или `git pull` он уже существует. Аналогично зафиксирован каталог `frontend` — там лежит учебная страница `index.html`, которую Nginx отдаёт до подключения приложения.

Файл `registry/auth/htpasswd` исключён из Git.

## Запуск

Запустите инфраструктуру:

```powershell
docker compose up -d
```

Проверьте состояние сервисов:

```powershell
docker compose ps
```

Остановите сервисы без удаления данных:

```powershell
docker compose down
```

Данные PostgreSQL, pgAdmin и Registry сохраняются в Docker volumes. Для полного удаления данных используйте `docker compose down -v`; эта команда удаляет все данные сервисов безвозвратно.

## HTTP Docker Registry

Registry доступен по `http://IP_СЕРВЕРА:REGISTRY_PORT`. В учебном проекте он работает без TLS, поэтому его следует использовать только в доверенной локальной сети.

На каждой машине, откуда будут отправляться образы, добавьте адрес Registry в настройку Docker daemon `insecure-registries`. Для Docker Desktop на Windows откройте **Settings → Docker Engine** и добавьте адрес в конфигурацию:

```json
{
  "insecure-registries": ["192.168.1.10:5000"]
}
```

Подставьте значения `REGISTRY_HOST` и `REGISTRY_PORT` из `.env`, затем примените настройки Docker Desktop. После этого выполните вход:

```powershell
docker login 192.168.1.10:5000
```

Публикация тестового образа:

```powershell
docker pull alpine:3.20
docker tag alpine:3.20 192.168.1.10:5000/orders-backend:test
docker push 192.168.1.10:5000/orders-backend:test
docker pull 192.168.1.10:5000/orders-backend:test
```

Проверка доступности API Registry без аутентификации должна вернуть ответ `401 Unauthorized`, что означает включённую аутентификацию:

```powershell
Invoke-WebRequest http://192.168.1.10:5000/v2/ -SkipHttpErrorCheck
```

Не используйте HTTP Registry в публичной сети: логин и пароль `docker login` передаются без шифрования. Для неучебной эксплуатации необходим TLS.

## Watchtower

Watchtower проверяет образы каждые пять минут и обновляет только контейнеры с меткой:

```yaml
labels:
  com.centurylinklabs.watchtower.enable: "true"
```

В текущей конфигурации эта метка указана только в закомментированном шаблоне будущего backend. Инфраструктурные сервисы автоматически не обновляются.
