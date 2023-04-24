### Запуск

1. Выставляем переменные окружения:
```
DEPLOY_TARGET_SERVER - сервер для деплоя обновления

DEPLOY_TEAMCITY - Ссылка на тимсити

DEPLOY_TEAMCITY_USER - Пользователь тимсити

DEPLOY_TEAMCITY_PASSWORD - Пароль пользователя тимсити

DEPLOY_TEAMCITY_BUILD_CONF - Конфигурация сборки(билда)

DEPLOY_GITHUB_ACCESS_TOKEN - Токен Github

DEPLOY_GITHUB_REPO - Ссылка на репозиторий Github

IS_PRERELEASE - булева-переменная, отвечает за то, что загружать пререлиз или нет

TG_BOT_TOKEN - Токен бота для оповещений из botFather

TG_BOT_CHAT_ID - id чата куда придут оповещения

RETAILROTOR_REGISTRY_URL - ссылка на хранилище образов
```
2. Собираем образ: `docker build . --tag tp_deploy`
3. Запускаем контейнер: `docker run --name=tp_deploy -d tp_deploy`
4. (Необ.) Запуск изнутри контейнера: `/venv/bin/poetry run python3 -m tp_deploy_bot`