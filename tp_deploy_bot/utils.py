import time

from semver import Version as SemVer
import requests
import re
import telebot

from tp_deploy_bot.config import (
    TG_BOT_TOKEN,
    TG_BOT_CHAT_ID,
    TEAMCITY_STATUS_TEXT,
    TEAMCITY_MAX_REQUEST_COUNT,
)

VERSION_RE = re.compile(
    r"<title>RetailRotor (\d+[.]\d[.]\d(-rc\d)?)</title>", re.MULTILINE
)


def get_server_version(target_server: str) -> SemVer:
    response = requests.get(f"https://{target_server}/")
    response.raise_for_status()
    version = VERSION_RE.search(response.text)
    version = version.group(1)
    return SemVer.parse(version)


def get_latest_release(github, repo_name, prerelease=False) -> SemVer:
    repo = github.get_repo(repo_name)
    latest_release = SemVer(0, 0, 0)
    for release in repo.get_releases():
        if prerelease != release.prerelease:
            continue
        release_version = SemVer.parse(release.tag_name)
        if release_version > latest_release:
            latest_release = release_version
            break
    return latest_release


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
    bot = telebot.TeleBot(TG_BOT_TOKEN, parse_mode="HTML")
    pre_launch_message = f"Запуск обновления {tag} для сервера {target_server}"
    bot.send_message(TG_BOT_CHAT_ID, pre_launch_message)
    response = teamcity.build_queue_api.queue_new_build(body=build, move_to_top=False)
    time.sleep(5.0)
    build_id = response.id
    response = wait_for_build_end(teamcity, build_id)
    response_message = (
        f"[BUILD:{build_id}]Сборка обновления {tag} для сервера {target_server} окончилась"
        f"\nстатус: <b>{response.status_text}</b>"
        f"\nсм. подробности по <a href='{response.web_url}'>ссылке</a>"
    )
    bot.send_message(TG_BOT_CHAT_ID, response_message)
