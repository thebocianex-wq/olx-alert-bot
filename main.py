import requests

url = "https://www.olx.pl/oferty/q-kukirin-g4/rss/"

r = requests.get(url)

print("STATUS:", r.status_code)
print("LEN:", len(r.text))
print(r.text[:500])
