# 🇵🇰 Pakistani OTT Live Channel Scraper

A Python-based scraper to extract live TV channel stream URLs from Pakistani OTT platforms.

> ⚠️ **Disclaimer**: This project is intended for **personal, educational, and research purposes only**. Respect each platform's Terms of Service. Do not use for commercial redistribution of content.

---

## 📺 Supported Platforms

| Platform | URL | Status |
|----------|-----|--------|
| Tamasha | [tamasha.tv](https://tamasha.tv) | ✅ Supported |
| Tapmad | [tapmad.com](https://tapmad.com) | ✅ Supported |
| MyCo | [myco.com.pk](https://myco.com.pk) | ✅ Supported |

---

## 🚀 Features

- 🔴 Extract live HLS/DASH stream URLs
- 📋 Export to M3U playlist format
- 🗂️ Export to JSON for custom integrations
- 🔁 Scheduled auto-refresh (streams expire)
- 🧩 Modular scraper design — easy to add new platforms
- 🔒 Optional login support for premium streams

---

## 📁 Project Structure

```
pak-ott-scraper/
├── scrapers/
│   ├── __init__.py
│   ├── base.py          # Abstract base scraper class
│   ├── tamasha.py       # Tamasha.tv scraper
│   ├── tapmad.py        # Tapmad.com scraper
│   └── myco.py          # MyCo.com.pk scraper
├── utils/
│   ├── __init__.py
│   ├── m3u_exporter.py  # Export channels to M3U playlist
│   ├── json_exporter.py # Export channels to JSON
│   └── helpers.py       # Shared utility functions
├── output/              # Generated M3U/JSON files saved here
├── docs/
│   ├── tamasha.md       # Platform-specific notes
│   ├── tapmad.md
│   └── myco.md
├── main.py              # CLI entry point
├── config.py            # Configuration (headers, tokens, timeouts)
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## ⚙️ Installation

```bash
git clone https://github.com/yourusername/pak-ott-scraper.git
cd pak-ott-scraper

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env          # Add credentials if needed
```

---

## 🖥️ Usage

### Scrape all platforms
```bash
python main.py --all
```

### Scrape a specific platform
```bash
python main.py --platform tamasha
python main.py --platform tapmad
python main.py --platform myco
```

### Export formats
```bash
python main.py --all --format m3u        # Save as playlist.m3u
python main.py --all --format json       # Save as channels.json
python main.py --all --format both       # Save both (default)
```

### Output to custom path
```bash
python main.py --all --output ./my-playlist.m3u
```

---

## 📄 Output Example (M3U)

```m3u
#EXTM3U
#EXTINF:-1 tvg-id="geo-news" tvg-name="Geo News" tvg-logo="https://..." group-title="News",Geo News
https://stream.tamasha.tv/live/geo-news/index.m3u8

#EXTINF:-1 tvg-id="ary-news" tvg-name="ARY News" tvg-logo="https://..." group-title="News",ARY News
https://cdn.tapmad.com/live/ary/playlist.m3u8
```

---

## 📄 Output Example (JSON)

```json
[
  {
    "id": "geo-news",
    "name": "Geo News",
    "platform": "tamasha",
    "category": "News",
    "logo": "https://...",
    "stream_url": "https://stream.tamasha.tv/live/geo-news/index.m3u8",
    "drm": false,
    "refreshed_at": "2025-01-01T12:00:00Z"
  }
]
```

---

## 🔧 Configuration (`config.py`)

```python
REQUEST_TIMEOUT = 15       # seconds
RETRY_ATTEMPTS = 3
STREAM_REFRESH_INTERVAL = 3600  # seconds (1 hour)
USER_AGENT = "Mozilla/5.0 ..."
```

---

## 🧩 Adding a New Platform

1. Create `scrapers/newplatform.py` extending `BaseScraper`
2. Implement `get_channels()` and `get_stream_url(channel_id)`
3. Register it in `scrapers/__init__.py`
4. Add to the platform map in `main.py`

See [docs/adding-platform.md](docs/adding-platform.md) for full guide.

---

## 🛠️ Tech Stack

- **Python 3.9+**
- `requests` / `httpx` — HTTP client
- `playwright` or `selenium` — JS-rendered pages
- `beautifulsoup4` — HTML parsing
- `m3u8` — M3U playlist handling
- `python-dotenv` — Environment config
- `rich` — Pretty CLI output

---

## 🤝 Contributing

PRs welcome! Please:
- Follow the `BaseScraper` interface
- Add platform docs under `/docs`
- Test before submitting

---

## 📜 License

MIT License. See [LICENSE](LICENSE).
