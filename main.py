#!/usr/bin/env python3
"""
Pakistani OTT Live TV Channel Scraper
Scrapes live TV channels from Tamasha, Tapmad, MyCo, ShoqPK
Auto-updates every 30 minutes, removes dead links, adds new ones.
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from scrapers.tamasha import TamashaScraer
from scrapers.tapmad import TapmadScraper
from scrapers.myco import MyCoScraper
from scrapers.shoqpk import ShoqPKScraper
from utils.validator import ChannelValidator
from utils.m3u_builder import M3UBuilder
from utils.logger import setup_logger

# ── Config ────────────────────────────────────────────────────────────────────
OUTPUT_DIR = Path("output")
LOGS_DIR   = Path("logs")
UPDATE_INTERVAL_MINS = 30

SCRAPERS = [
    TamashaScraer,
    TapmadScraper,
    MyCoScraper,
    ShoqPKScraper,
]

logger = setup_logger("main")


async def run_scraper(scraper_class):
    """Run a single scraper and return its channels."""
    scraper = scraper_class()
    name = scraper.name
    try:
        logger.info(f"[{name}] Starting scrape…")
        channels = await scraper.scrape()
        logger.info(f"[{name}] Found {len(channels)} channels")
        return channels
    except Exception as exc:
        logger.error(f"[{name}] Scraper failed: {exc}")
        return []


async def validate_channels(channels):
    """Validate all channels concurrently, removing dead streams."""
    validator = ChannelValidator()
    logger.info(f"Validating {len(channels)} channels…")
    live_channels = await validator.validate_all(channels)
    dead = len(channels) - len(live_channels)
    logger.info(f"Validation complete: {len(live_channels)} live, {dead} dead (removed)")
    return live_channels


def load_existing_channels():
    """Load previously saved channels for diff/merge."""
    path = OUTPUT_DIR / "channels.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return []


def save_channels(channels):
    """Persist channels to JSON and M3U files."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    # JSON
    json_path = OUTPUT_DIR / "channels.json"
    with open(json_path, "w") as f:
        json.dump(channels, f, indent=2, ensure_ascii=False)

    # M3U playlist
    m3u_path = OUTPUT_DIR / "channels.m3u"
    M3UBuilder.write(channels, m3u_path)

    # Per-source M3U files
    sources = {}
    for ch in channels:
        sources.setdefault(ch.get("source", "unknown"), []).append(ch)
    for src, chs in sources.items():
        M3UBuilder.write(chs, OUTPUT_DIR / f"{src.lower()}.m3u")

    # Stats / metadata
    meta = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "total_channels": len(channels),
        "sources": {src: len(chs) for src, chs in sources.items()},
    }
    with open(OUTPUT_DIR / "meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    logger.info(f"Saved {len(channels)} channels → {OUTPUT_DIR}/")
    return meta


async def scrape_cycle():
    """One full scrape → validate → save cycle."""
    logger.info("=" * 60)
    logger.info(f"Scrape cycle started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. Scrape all sources concurrently
    tasks = [run_scraper(cls) for cls in SCRAPERS]
    results = await asyncio.gather(*tasks)

    # 2. Merge, deduplicate by stream URL
    seen_urls = set()
    all_channels = []
    for channel_list in results:
        for ch in channel_list:
            url = ch.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                all_channels.append(ch)

    logger.info(f"Total unique channels after merge: {len(all_channels)}")

    # 3. Validate (remove dead streams)
    live_channels = await validate_channels(all_channels)

    # 4. Load previous, detect diff
    old_channels = load_existing_channels()
    old_urls = {ch["url"] for ch in old_channels}
    new_urls  = {ch["url"] for ch in live_channels}
    added   = new_urls - old_urls
    removed = old_urls - new_urls
    logger.info(f"Diff → +{len(added)} new, -{len(removed)} removed")

    # 5. Sort by source then name
    live_channels.sort(key=lambda c: (c.get("source", ""), c.get("name", "")))

    # 6. Save
    meta = save_channels(live_channels)
    meta["added"]   = len(added)
    meta["removed"] = len(removed)

    logger.info("Scrape cycle complete.")
    return meta


async def watch_loop():
    """Continuous loop: scrape every UPDATE_INTERVAL_MINS minutes."""
    while True:
        try:
            await scrape_cycle()
        except Exception as exc:
            logger.exception(f"Cycle crashed: {exc}")
        logger.info(f"Next update in {UPDATE_INTERVAL_MINS} minutes…")
        await asyncio.sleep(UPDATE_INTERVAL_MINS * 60)


def main():
    LOGS_DIR.mkdir(exist_ok=True)
    if "--once" in sys.argv:
        # Single run (used by GitHub Actions)
        asyncio.run(scrape_cycle())
    else:
        # Continuous daemon mode
        asyncio.run(watch_loop())


if __name__ == "__main__":
    main()
