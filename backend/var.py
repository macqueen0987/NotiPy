import os

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
