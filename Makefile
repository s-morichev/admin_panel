include .env

dev-new:
	docker compose -f docker-compose.dev.yaml up -d --build
	sleep 3  # wait for container startup
	docker compose -f docker-compose.dev.yaml exec movies_admin python manage.py migrate --fake-initial --no-input
	docker compose -f docker-compose.dev.yaml exec -e DJANGO_SUPERUSER_PASSWORD=${POSTGRES_PASSWORD} movies_admin python manage.py createsuperuser --username ${POSTGRES_USER} --email admin@example.com --no-input
	docker compose -f docker-compose.dev.yaml exec movies_admin python ./sqlite_to_postgres/load_data.py

dev-up:
	docker compose -f docker-compose.dev.yaml up -d

dev-down:
	docker compose -f docker-compose.dev.yaml down

dev-down-v:
	docker compose -f docker-compose.dev.yaml down -v

dev-logs:
	docker compose -f docker-compose.dev.yaml logs -f

dev-psql:
	env PGOPTIONS=${POSTGRES_OPTIONS} psql -h 127.0.0.1 -U ${POSTGRES_USER} -d ${POSTGRES_DB_NAME}

build-admin:
	docker --log-level=debug build --file=docker/movies_admin/Dockerfile --tag=movies_admin_sprint_3 --target=production .

build-etl:
	docker --log-level=debug build --file=docker/etl/Dockerfile --tag=etl_sprint_3 --target=production .

build-db:
	docker --log-level=debug build --tag=postgres_sprint_3 ./docker/postgres/

build-nginx:
	docker --log-level=debug build --tag=nginx_sprint_3 ./docker/nginx/

build-all: build-admin build-etl build-db build-nginx

prod-new: build-all
	docker compose up -d
	sleep 3  # wait for container startup
	docker compose exec -u 0 movies_admin python manage.py collectstatic --no-input
	docker compose exec movies_admin python manage.py migrate --fake-initial --no-input
	docker compose exec -e DJANGO_SUPERUSER_PASSWORD=${POSTGRES_PASSWORD} movies_admin python manage.py createsuperuser --username ${POSTGRES_USER} --email admin@example.com --no-input
	docker compose exec movies_admin python ./sqlite_to_postgres/load_data.py
