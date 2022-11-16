# Базовый образ с общими системными зависимостями для dev и prod
FROM python:3.10.8-slim as python-base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONPATH="/opt/app:$PYTHONPATH" \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

RUN apt-get update \
    && apt-get --no-install-recommends install -y \
    libpq5 \
    netcat \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Билдер для установки Python пакетов и необходимых системных зависимостей
FROM python-base as builder-base
RUN apt-get update \
    && apt-get --no-install-recommends install -y \
    curl \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка Poetry в папку POETRY_HOME с учетом версии
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl -sSL https://install.python-poetry.org | POETRY_VERSION=1.2.2 python3 -

# Устанавливаем Python пакеты для продакшена
WORKDIR $PYSETUP_PATH
COPY ./poetry.lock ./pyproject.toml ./
RUN poetry install --only main,movies_admin --no-root

# development образ
FROM python-base as development

# Копируем Poetry и Python пакеты для продакшена из билдера
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

# Устанавливаем остальные Python пакеты
WORKDIR $PYSETUP_PATH
RUN poetry install --without etl --no-root

COPY ./docker/movies_admin/entrypoint.sh ./docker/wait-for /opt/
RUN chmod +x /opt/entrypoint.sh /opt/wait-for

WORKDIR /opt/app
COPY ./movies_admin .

EXPOSE 8000
ENTRYPOINT ["/opt/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# 'production' образ
FROM python-base as production

# Копируем только Python пакеты (без Poetry)
COPY --from=builder-base $VENV_PATH $VENV_PATH

COPY ./docker/movies_admin/entrypoint.sh ./docker/wait-for /opt/
RUN chmod +x /opt/entrypoint.sh /opt/wait-for

WORKDIR /opt/app
COPY ./movies_admin .

RUN groupadd -r app && useradd -d /opt/app -r -g app app \
    && chown -R app:app /opt/app
USER app

EXPOSE 8000
ENTRYPOINT ["/opt/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]