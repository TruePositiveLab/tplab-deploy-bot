FROM python:3.10-slim as os-base

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
RUN apt-get update



FROM os-base as app-base
ENV VENV_PATH=/venv
RUN python3 -m venv $VENV_PATH
RUN $VENV_PATH/bin/pip install -U pip setuptools
RUN $VENV_PATH/bin/pip install poetry
RUN $VENV_PATH/bin/poetry config virtualenvs.create false

ARG APPDIR=/app
ENV DEPLOY_TARGET_SERVER \
    DEPLOY_GITHUB_ACCESS_TOKEN \
    DEPLOY_GITHUB_REPO \
    IS_PRERELEASE \
    DEPLOY_TEAMCITY \
    DEPLOY_TEAMCITY_USER \
    DEPLOY_TEAMCITY_PASSWORD \
    DEPLOY_TEAMCITY_BUILD_CONF \
    TG_BOT_TOKEN \
    TG_BOT_CHAT_ID
WORKDIR $APPDIR/
COPY tp_deploy_bot ./tp_deploy_bot
COPY pyproject.toml ./pyproject.toml
RUN $VENV_PATH/bin/poetry install --no-dev

FROM app-base as main

CMD $VENV_PATH/bin/poetry run python3 -m tp_deploy_bot
