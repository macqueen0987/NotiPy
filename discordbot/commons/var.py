import os

token = os.environ["DISCORD_TOKEN"]

devserver = os.environ['DISCORD_DEVSERVER']  # Replace with actual server ID

developers = os.environ['DISCORD_DEVELOPERS']  # Replace with actual developer IDs


# logfiles, they will be located at discordbot/logs
debugfile = os.environ['DISCORD_DEBUG_FILE']  # File to log debug information
errfile = os.environ['DISCORD_ERROR_LOG']  # File to log error information

app_root = "/discord"
