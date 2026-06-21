import os
import json
import re
import requests
from playwright.sync_api import sync_playwright

print("NOWA WERSJA BOTA")

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

SEARCHES = [
    {"name": "hulajnoga elektryczna dualtron"},
    {"name": "Axxo"},
    {"name": "Grand Fitness"},
    {"name": "Eleiko"},
    {"name": "sztanga Samtek"},
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
            "disable_web_page_preview": True,
        },
        timeout=20,
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

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0 Safari/537.36"
    )

    for search in SEARCHES:

        try:

            query = search["name"]

            url = f"https://www.olx.pl/oferty/q-{query.replace(' ', '-')}/"

            print(f"\nSprawdzam: {query}")

            page.goto(
                url,
                wait_until="networkidle",
                timeout=60000
            )

            offers = page.locator('a[href*="/d/oferta/"]')

            count = min(offers.count(), 10)

            for i in range(count):

                offer = offers.nth(i)

                try:
                    title = offer.inner_text().strip()
                except:
                    title = ""

                try:
                    full_text = offer.locator("xpath=..").inner_text()
                except:
                    full_text = title

                link = offer.get_attribute("href")

                if not link:
                    continue

                if link.startswith("/"):
                    link = "https://www.olx.pl" + link

                if link in seen:
                    continue

                # SZUKANIE CENY
                price = None
                price_text = "brak ceny"

                match = re.search(
                    r'(\d[\d ]*)\s*zł',
                    full_text,
                    re.IGNORECASE
                )

                if match:
                    price_text = match.group(0)
                    price = int(
                        match.group(1)
                        .replace(" ", "")
                    )

                print("TITLE:", title)
                print("PRICE:", price)
                print("LIMIT:", search.get("max_price"))

                # FILTR CENOWY
                if "max_price" in search:

                    if price is None:
                        print("BRAK CENY - POMINIĘTO")
                        continue

                    if price > search["max_price"]:
                        print(
                            f"POMINIĘTO: {title} | "
                            f"{price} zł > "
                            f"{search['max_price']} zł"
                        )
                        continue

                msg = (
                    f"🔥 {query}\n\n"
                    f"📦 {title}\n"
                    f"💰 {price_text}\n\n"
                    f"🔗 {link}"
                )

                send(msg)

                print("WYSŁANO:", title)

                seen.add(link)

        except Exception as e:
            print("BŁĄD:", query, e)

    browser.close()

save_seen(seen)

print("OK")
