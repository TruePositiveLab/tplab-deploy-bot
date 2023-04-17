import os
from dotenv import load_dotenv
from github import Github
from dohq_teamcity import TeamCity

load_dotenv()

env = os.environ

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
IS_PRERELEASE = env.get("IS_PRERELEASE", "False").lower() in ("true", "1", "t")

# Telegram notifications conf
TG_BOT_TOKEN = env["TG_BOT_TOKEN"]
TG_BOT_CHAT_ID = env["TG_BOT_CHAT_ID"]
