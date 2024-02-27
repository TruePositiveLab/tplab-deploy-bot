import time

import backoff as backoff
import dohq_teamcity
from requests.auth import HTTPBasicAuth
from semver import Version as SemVer
import requests
import re
import telebot
from telebot.formatting import escape_markdown

from tp_deploy_bot.config import (
    TG_BOT_TOKEN,
    TG_BOT_CHAT_ID,
    TEAMCITY_STATUS_TEXT,
    TEAMCITY_MAX_REQUEST_COUNT, RETAILROTOR_REGISTRY_URL,
    REGISTRY_PASSWORD,
    REGISTRY_LOGIN
)

VERSION_RE = re.compile(
    r"<title>RetailRotor (\d+[.]\d[.]\d(-rc\d{1,3})?)</title>", re.MULTILINE
)


def teamcity_exception_handler(func):
    def inner_function(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except dohq_teamcity.ApiException as exc:
            send_tg_bot_message(f"Ошибка подключения к API Teamcity\n{exc.body}")
        except Exception as exc:
            send_tg_bot_message(f"Неизвестная ошибка\n{exc}")
    return inner_function


def get_server_version(target_server: str) -> SemVer:
    response = requests.get(f"https://{target_server}/")
    response.raise_for_status()
    version = VERSION_RE.search(response.text)
    version = version.group(1)
    return SemVer.parse(version)


def get_latest_release(github, repo_name, prerelease=False) -> SemVer:
    repo = github.get_repo(repo_name)
    latest_release = SemVer(0, 0, 0)
    release_body = ""
    for release in repo.get_releases():
        if prerelease != release.prerelease:
            continue
        release_version = SemVer.parse(release.tag_name)
        if release_version > latest_release:
            latest_release = release_version
            release_body = release.body
            break
    if release_body == "":
        release_body = "Ошибка поиска последней доступной версии, ничего не найдено!"

    return latest_release, release_body


@backoff.on_exception(backoff.expo,
                      dohq_teamcity.ApiException,
                      max_time=120)
def wait_for_build_end(teamcity, build_id):
    locator = f"id:{build_id}"
    response = teamcity.build_queue_api.get_build(locator)
    requests_limit = TEAMCITY_MAX_REQUEST_COUNT
    for _ in range(requests_limit):
        if response.status_text in TEAMCITY_STATUS_TEXT:
            break
        time.sleep(60)
        response = teamcity.build_queue_api.get_build(locator)
    return response


@backoff.on_exception(backoff.expo,
                      dohq_teamcity.ApiException,
                      max_time=120)
def start_new_build(teamcity, build):
    return teamcity.build_queue_api.queue_new_build(body=build, move_to_top=False)


@teamcity_exception_handler
def queue_deploy(teamcity, conf_id, target_server, tag):
    build = {
        "buildType": {"id": conf_id},
        "properties": {
            "property": [
                {"name": "env.PRODUCTION", "value": target_server},
                {"name": "env.REROTOR_BRANCH", "value": f"{tag}"},
                {"name": "SKIP_BACKUP", "value": True},
            ]
        },
    }
    response = start_new_build(teamcity, build)
    pre_launch_message = (f"Запуск обновления {tag} для сервера {target_server}" \
                          f"\nсм. подробности по {response.web_url}")
    send_tg_bot_message(pre_launch_message)
    build_id = response.id
    response = wait_for_build_end(teamcity, build_id)

    response_message = (
        f"[BUILD:{build_id}]\nСборка обновления {tag} для сервера {target_server} окончилась"
        f"\nстатус: {response.status_text}"
        f"\nсм. подробности по {response.web_url}"
    )
    send_tg_bot_message(response_message)


def send_tg_bot_message(message: str):
    bot = telebot.TeleBot(TG_BOT_TOKEN)
    message = escape_markdown(message)
    bot.send_message(TG_BOT_CHAT_ID, message, parse_mode="MarkdownV2")


def check_image_on_registry(release_tag):
    registry_url = RETAILROTOR_REGISTRY_URL
    response = requests.get(registry_url, verify=False, auth=HTTPBasicAuth(REGISTRY_LOGIN, REGISTRY_PASSWORD))
    response.raise_for_status()
    tags = response.json()['tags']
    return str(release_tag) in tags
