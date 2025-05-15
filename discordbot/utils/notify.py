import requests

def send_discord_message(content: str, webhook_url: str):
    data = {"content": content}
    response = requests.post(webhook_url, json=data)
    return response.status_code == 204