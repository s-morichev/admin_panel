## Проект для задания по 3 спринту.

Решение по ETL находится в папке /postgres_to_es. 

### Локальная разработка (development)

При первоначальном запуске командой `make dev-new` происходит сборка образов и запуск
контейнеров, применение миграций, создание суперпользователя и копирование данных из
SQLite в PostgreSQL. Имя пользователя и пароль для базы данных и суперпользователя
совпадают. Через несколько секунд после старта (зависит от настроек backoff) etl
загружает данные в Elasticsearch, загрузку можно проверить по логам `docker compose -f 
docker-compose.dev.yaml logs etl -f`.

Команды:
- Первоначальный запуск development-сервера:
  - `make dev-new`
- Запуск development-сервера:
  - `make dev-up`
- Остановка и удаление запущенных контейнеров:
  - `make dev-down`
- Остановка и удаление контейнеров вместе с томами:
  - `make dev-down-v`
- Просмотр логов:
  - `make dev-logs`
- Подключение к postgres:
  - `make dev-psql`

### Запуск "production" на локальной машине

Не забудьте изменить в .env файле `DEBUG=False`

*Для запуска на локальной машине можно воспользоваться командой `make prod-new`. Она
последовательно выполняет перечисленные ниже команды.*

- Соберите образы `make build-all`
- Запустите контейнеры `docker compose up -d`

При необходbмости соберите статику, примените миграции, создайте суперпользователя, 
скопируйте данные:

`docker compose exec -u 0 movies_admin python manage.py collectstatic --no-input`
`docker compose exec app python manage.py migrate --fake-initial`  
`docker compose exec app python manage.py createsuperuser`  
`docker compose exec app python ./sqlite_to_postgres/load_data.py`  
