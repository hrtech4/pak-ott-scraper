# 📺 Pakistani OTT Live TV Scraper

> Auto-scrapes live TV channels from Pakistani streaming platforms — updated every **30 minutes** via GitHub Actions.

![Live Channels](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/YOUR_USERNAME/pk-ott-scraper/main/output/badge.json&style=flat-square)
![Update Status](https://img.shields.io/github/actions/workflow/status/YOUR_USERNAME/pk-ott-scraper/update.yml?style=flat-square&label=Auto-Update)
![License](https://img.shields.io/github/license/YOUR_USERNAME/pk-ott-scraper?style=flat-square)

---

## 🎯 Sources

| Platform | URL | Status |
|----------|-----|--------|
| **Tamasha** | tamasha.tv | ✅ Active |
| **Tapmad** | tapmad.com | ✅ Active |
| **MyCo** | myco.io | ✅ Active |
| **ShoqPK** | shoq.pk | ✅ Active |

---

## 📁 Output Files

All files are in the [`output/`](./output/) directory:

| File | Description |
|------|-------------|
| `channels.m3u` | Combined M3U playlist (all sources) |
| `tamasha.m3u` | Tamasha channels only |
| `tapmad.m3u` | Tapmad channels only |
| `myco.m3u` | MyCo channels only |
| `shoqpk.m3u` | ShoqPK channels only |
| `channels.json` | Full JSON with metadata |
| `meta.json` | Stats: total, per-source counts, last update time |

### 📡 M3U Playlist URLs (use in any IPTV player)

```
# All channels
https://raw.githubusercontent.com/YOUR_USERNAME/pk-ott-scraper/main/output/channels.m3u

# Tamasha only
https://raw.githubusercontent.com/YOUR_USERNAME/pk-ott-scraper/main/output/tamasha.m3u

# Tapmad only
https://raw.githubusercontent.com/YOUR_USERNAME/pk-ott-scraper/main/output/tapmad.m3u

# MyCo only
https://raw.githubusercontent.com/YOUR_USERNAME/pk-ott-scraper/main/output/myco.m3u

# ShoqPK only
https://raw.githubusercontent.com/YOUR_USERNAME/pk-ott-scraper/main/output/shoqpk.m3u
```

---

## ✨ Features

- 🕷️ **Multi-source scraping** — Tamasha, Tapmad, MyCo, ShoqPK
- ✅ **Dead link removal** — every stream is validated (HTTP + M3U check)
- 🔄 **Auto-update** — GitHub Actions cron runs every 30 minutes
- 🆕 **New channel detection** — diff logged on each cycle
- 📋 **M3U + JSON output** — works in VLC, Kodi, TiviMate, OTT Navigator
- 🪵 **Rotating logs** — stored in `logs/` (5 MB × 3 files)

---

## 🚀 Quick Start

### Run locally (one-shot)
```bash
git clone https://github.com/YOUR_USERNAME/pk-ott-scraper
cd pk-ott-scraper
pip install -r requirements.txt
python main.py --once
```

### Run as daemon (updates every 30 min)
```bash
python main.py
```

### Docker
```bash
docker build -t pk-ott-scraper .
docker run --rm -v $(pwd)/output:/app/output pk-ott-scraper
```

---

## 🏗️ Project Structure

```
pk-ott-scraper/
├── main.py                  # Orchestrator
├── requirements.txt
├── Dockerfile
├── scrapers/
│   ├── base.py              # Base scraper class
│   ├── tamasha.py           # Tamasha.tv scraper
│   ├── tapmad.py            # Tapmad.com scraper
│   ├── myco.py              # MyCo.io scraper
│   └── shoqpk.py            # ShoqPK.pk scraper
├── utils/
│   ├── validator.py         # Async HLS stream validator
│   ├── m3u_builder.py       # M3U playlist writer
│   └── logger.py            # Rotating file logger
├── scripts/
│   ├── commit_summary.py    # CI commit message helper
│   └── gen_badge.py         # README badge generator
├── .github/
│   └── workflows/
│       └── update.yml       # Auto-update GitHub Action
└── output/                  # Generated (committed by CI)
    ├── channels.m3u
    ├── channels.json
    ├── meta.json
    └── badge.json
```

---

## ⚙️ GitHub Actions Setup

The workflow runs automatically. No secrets needed — it uses the built-in `GITHUB_TOKEN`.

To enable write access:
1. Go to **Settings → Actions → General**
2. Set **Workflow permissions** to **"Read and write permissions"**

To trigger manually: **Actions → 🔄 Auto-Update Channels → Run workflow**

---

## 🔌 IPTV Player Setup

| Player | How to add |
|--------|-----------|
| **VLC** | Media → Open Network Stream → paste M3U URL |
| **Kodi** | PVR IPTV Simple Client → M3U playlist URL |
| **TiviMate** | Add playlist → paste M3U URL |
| **OTT Navigator** | Add source → M3U URL |
| **GSE Smart IPTV** | Remote Playlists → paste M3U URL |

---

## ⚠️ Legal Disclaimer

This tool scrapes **publicly accessible** stream endpoints from OTT platforms for **personal/research use only**. Respect each platform's Terms of Service. The maintainers are not responsible for misuse. Commercial redistribution of scraped content is prohibited.

---

## 🤝 Contributing

PRs welcome! To add a new source:
1. Create `scrapers/newsource.py` extending `BaseScraper`
2. Add it to `SCRAPERS` list in `main.py`
3. Submit a PR

---

*Auto-updated by GitHub Actions • Last update visible in `output/meta.json`*
