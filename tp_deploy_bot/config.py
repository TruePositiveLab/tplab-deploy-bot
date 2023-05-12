import ast
import os
from dotenv import load_dotenv
from github import Github
from dohq_teamcity import TeamCity

load_dotenv()

env = os.environ


def boolean_env(key, default=False):
    val = env.get(key, "True" if default else "False")
    try:
        return ast.literal_eval(val)
    except:  # noqa
        return default


RETAILROTOR_REGISTRY_URL = env["RETAILROTOR_REGISTRY_URL"]
REGISTRY_LOGIN = env["REGISTRY_LOGIN"]
REGISTRY_PASSWORD = env["REGISTRY_PASSWORD"]

TARGET_SERVER = env["DEPLOY_TARGET_SERVER"]
# Teamcity conf
TEAMCITY = TeamCity(
    env["DEPLOY_TEAMCITY"],
    auth=(env["DEPLOY_TEAMCITY_USER"], env["DEPLOY_TEAMCITY_PASSWORD"]),
)
TEAMCITY_BUILD_CONF_ID = env["DEPLOY_TEAMCITY_BUILD_CONF"]
TEAMCITY_STATUS_TEXT = ["Failed", "Success"]
TEAMCITY_MAX_REQUEST_COUNT = 30

# Github conf
GITHUB = Github(env["DEPLOY_GITHUB_ACCESS_TOKEN"])
GITHUB_REPO = env["DEPLOY_GITHUB_REPO"]
IS_PRERELEASE = boolean_env("IS_PRERELEASE")

# Telegram notifications conf
TG_BOT_TOKEN = env["TG_BOT_TOKEN"]
TG_BOT_CHAT_ID = env["TG_BOT_CHAT_ID"]
