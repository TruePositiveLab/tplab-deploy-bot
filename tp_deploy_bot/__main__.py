import sys

from tp_deploy_bot.config import (
    TARGET_SERVER,
    TEAMCITY,
    TEAMCITY_BUILD_CONF_ID,
    GITHUB,
    GITHUB_REPO,
    IS_PRERELEASE,
)
from tp_deploy_bot.utils import get_server_version, get_latest_release, queue_deploy, send_tg_bot_message


def main():
    server_version = get_server_version(TARGET_SERVER)
    print(f"{TARGET_SERVER} version is {server_version}")
    is_prerelease = bool(server_version.prerelease)
    print(f"Prerelease status: {is_prerelease}")
    new_version = get_latest_release(GITHUB, GITHUB_REPO, prerelease=IS_PRERELEASE)
    print(f"Latest github release version: {new_version}")

    if new_version <= server_version:
        send_tg_bot_message(f"Версия на сервере {TARGET_SERVER} = {server_version} является самой актуальной")
        sys.exit(0)

    queue_deploy(TEAMCITY, TEAMCITY_BUILD_CONF_ID, TARGET_SERVER, new_version)


if __name__ == '__main__':
    main()
