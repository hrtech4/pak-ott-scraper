import requests

OUTPUT_FILE = "Tamasha.m3u"
CDN_BASE = "https://cdn22lhr.tamashaweb.com:8087/jazzauth"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
REFERER = "https://tamashaweb.com/"

CHANNELS = [
    {"slug": "ARYdigital",       "name": "ARY Digital",          "category": "Entertainment"},
    {"slug": "humtv",            "name": "HUM TV",               "category": "Entertainment"},
    {"slug": "BOLEntertainment", "name": "BOL Entertainment",    "category": "Entertainment"},
    {"slug": "GeoEntertainment", "name": "Geo Entertainment",    "category": "Entertainment"},
    {"slug": "GreenTV",          "name": "Green Entertainment",  "category": "Entertainment"},
    {"slug": "ExpressEnt",       "name": "Express Entertainment","category": "Entertainment"},
    {"slug": "APlus",            "name": "A Plus",               "category": "Entertainment"},
    {"slug": "urdu1",            "name": "Urdu 1",               "category": "Entertainment"},
    {"slug": "AryZindagi",       "name": "ARY Zindagi",          "category": "Entertainment"},
    {"slug": "HumSitaray",       "name": "HUM Sitaray",          "category": "Entertainment"},
    {"slug": "TVOne",            "name": "TV One",               "category": "Entertainment"},
    {"slug": "GeoNews",          "name": "Geo News",             "category": "News"},
    {"slug": "ARYNews",          "name": "ARY News",             "category": "News"},
    {"slug": "BOLNews",          "name": "BOL News",             "category": "News"},
    {"slug": "HumNews",          "name": "HUM News",             "category": "News"},
    {"slug": "SamaaNews",        "name": "Samaa TV",             "category": "News"},
    {"slug": "DunyaNews",        "name": "Dunya News",           "category": "News"},
    {"slug": "AajNews",          "name": "Aaj News",             "category": "News"},
    {"slug": "ExpressNews",      "name": "Express News",         "category": "News"},
    {"slug": "92News",           "name": "92 News",              "category": "News"},
    {"slug": "DawnNews",         "name": "Dawn News",            "category": "News"},
    {"slug": "PTVSports",        "name": "PTV Sports",           "category": "Sports"},
    {"slug": "GeoSuper",         "name": "Geo Super",            "category": "Sports"},
    {"slug": "ASports",          "name": "A Sports",             "category": "Sports"},
    {"slug": "PTVHome",          "name": "PTV Home",             "category": "General"},
    {"slug": "PTVNews",          "name": "PTV News",             "category": "News"},
    {"slug": "ARYQtv",           "name": "ARY Qtv",              "category": "Islamic"},
    {"slug": "PeaceTV",          "name": "Peace TV",             "category": "Islamic"},
]

def main():
    print("[*] Building Tamasha playlist...")
    lines = ["#EXTM3U"]

    for ch in CHANNELS:
        slug = ch["slug"]
        name = ch["name"]
        category = ch["category"]
        url = f"{CDN_BASE}/{slug}-abr/playlist.m3u8"

        lines.append(f'#EXTINF:-1 tvg-id="tamasha-{slug.lower()}" tvg-name="{name}" tvg-logo="" group-title="Tamasha - {category}",{name}')
        lines.append(f"#EXTVLCOPT:http-user-agent={USER_AGENT}")
        lines.append(f"#EXTVLCOPT:http-referrer={REFERER}")
        lines.append(url)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"[+] Saved: {OUTPUT_FILE} ({len(CHANNELS)} channels)")

if __name__ == "__main__":
    main()
