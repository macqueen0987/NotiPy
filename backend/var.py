import os
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")
NOTION_DB_ID = os.getenv("NOTION_DB_ID", "")

DISCORD_APP_ROOT = os.environ["DISCORD_APP_ROOT"]

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_API_ENDPOINT = os.environ["GITHUB_API_URL"]

DISCORD_API_ENDPOINT = os.environ["DISCORD_API_URL"]
CLIENT_ID = os.environ["DISCORD_CLIENT_ID"]
CLIENT_SECRET = os.environ["DISCORD_SECRET"]
REDIRECT_URI = os.environ["REDIRECT_URI"]

dbuser = os.environ["MYSQL_USER"]
dbpassword = os.environ["MYSQL_PASSWORD"]
dbhost = "notipy-database"
dbport = os.environ["MYSQL_TCP_PORT"]
dbname = os.environ["MYSQL_DATABASE"]

discordbot = "http://notipy-discordbot:9090"
