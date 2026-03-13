import json
import requests
from pathlib import Path

# load telegram config
config_path = Path("config/telegram.json")

with open(config_path, "r") as f:
    config = json.load(f)

BOT_TOKEN = config["bot_token"]
CHAT_ID = config["chat_id"]

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

payload = {
    "chat_id": CHAT_ID,
    "text": "Test: Telegram notifications working."
}

response = requests.post(url, json=payload)

print("Status:", response.status_code)
print("Response:", response.text)