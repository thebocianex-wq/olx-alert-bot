import os
import json
import requests
import xml.etree.ElementTree as ET

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

SEARCHES = [
    {"name": "hulajnoga elektryczna"},
    {"name": "Axxo"},
    {"name": "Grand Fitness"},
    {"name": "Eleiko"},
    {"name": "Samtek"},
    {"name": "obciążenie kalibrowane"},
    {"name": "talerze kalibrowane"},
    {"name": "Kukirin G2 Max", "max_price": 1600},
    {"name": "Kukirin G4", "max_price": 2200},
    {"name": "Ausom L2 Max Dual", "max_price": 2200},
    {"name": "Ausom L2 Dual Max", "max_price": 2200},
]

SEEN_FILE = "seen.json"

def send(msg):
    requests.get(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        params={
            "chat_id": CHAT_ID,
            "text": msg,
            "disable_web_page_preview": True
        }
    )

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

seen = load_seen()

for search in SEARCHES:

    query = search["name"]

    url = (
        "https://www.olx.pl/oferty/q-"
        + query.replace(" ", "-")
        + "/rss/"
    )

    try:
        r = requests.get(url, timeout=15)

        print("URL:", url)
        print("STATUS:", r.status_code)
        print(r.text[:500])

        root = ET.fromstring(r.content)

        for item in root.findall(".//item"):

            title = item.findtext("title", "")
            link = item.findtext("link", "")
            guid = item.findtext("guid", link)

            if guid in seen:
                continue

            msg = f"🔥 {query}\n\n{title}\n\n{link}"

            send(msg)
            seen.add(guid)

    except Exception as e:
        print("ERROR:", e)

save_seen(seen)

print("OK")
