# ✅ yes_client.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YESCALE_API_KEY")

YESCALE_CHAT_URL = "https://api.yescale.io/v1/chat/completions"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

def call_yescale(system_prompt: str, user_prompt: str, model="gpt-4o-mini-2024-07-18"):
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0
    }
    try:
        res = requests.post(YESCALE_CHAT_URL, headers=HEADERS, json=body)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"\u274c YesScale Error: {e}")
        return ""