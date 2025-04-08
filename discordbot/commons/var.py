import os

token = os.environ["DISCORD_TOKEN"]

devserver = os.environ["DISCORD_DEVSERVER"]  # Replace with actual server ID

# Replace with actual developer IDs
developers = os.environ["DISCORD_DEVELOPERS"]
developers = [int(dev) for dev in developers.split(",")]

# logfiles, they will be located at discordbot/logs
debugfile = os.environ["DISCORD_DEBUG_FILE"]  # File to log debug information
errfile = os.environ["DISCORD_ERROR_LOG"]  # File to log error information
apiport = os.environ["BACKEND_PORT"]

app_root = os.environ["DISCORD_APP_ROOT"]
backend_url = "http://notipy-backend"
backend_api_root = os.environ["BACKEND_APP_ROOT"]


api_root = f"{backend_url}:{apiport}{backend_api_root}"  # Backend API root URL

githuburl = "https://github.com"
