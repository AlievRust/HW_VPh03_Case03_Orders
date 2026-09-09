# История изменений

## 0001-docker-infrastructure

- Добавлена Docker Compose-инфраструктура с Nginx, PostgreSQL, pgAdmin, приватным HTTP Docker Registry и Watchtower.
- PostgreSQL изолирован во внутренней Docker-сети, а pgAdmin доступен через Nginx.
- Добавлены шаблон переменных окружения, исключение секретов Registry и инструкции по `docker login` и публикации образов.
