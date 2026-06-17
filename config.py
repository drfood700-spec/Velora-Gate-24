import json

with open("settings.json", "r", encoding="utf-8") as f:
    settings = json.load(f)

TOKEN = settings["bot_token"]
ADMIN_ID = settings["admin_id"]
