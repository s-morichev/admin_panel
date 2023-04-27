### Админ панель и ETL

Админ панель для добавления информации о фильмах и ETL по переносу этой информации
из postgres в elasticsearch

### Запуск

Переименуйте .env.sample в .env и выполните `make dev-new`

### Запуск "production" на локальной машине

Не забудьте изменить в .env файле `DEBUG=False`

- Соберите образы `make build-all`
- Запустите контейнеры `docker compose up -d`

При необходимости соберите статику, примените миграции, создайте суперпользователя, 
скопируйте данные:

- `docker compose exec -u 0 movies_admin python manage.py collectstatic --no-input`
- `docker compose exec app python manage.py migrate --fake-initial`  
- `docker compose exec app python manage.py createsuperuser`  
- `docker compose exec app python ./sqlite_to_postgres/load_data.py`  
