#!/usr/bin/env python3
"""
main.py — CLI entry point for the Pakistani OTT Live Channel Scraper.

Usage:
  python main.py --all
  python main.py --platform tamasha --format m3u
  python main.py --platform tapmad --output ./my.m3u
"""

import argparse
import os
from dotenv import load_dotenv
from scrapers import PLATFORM_MAP
from utils.m3u_exporter import export_m3u
from utils.json_exporter import export_json

load_dotenv()


def build_credentials(platform: str) -> dict:
    prefix = platform.upper()
    return {
        "email": os.getenv(f"{prefix}_EMAIL", ""),
        "password": os.getenv(f"{prefix}_PASSWORD", ""),
    }


def run(platforms: list[str], fmt: str, output: str | None):
    all_channels = []

    for platform_name in platforms:
        cls = PLATFORM_MAP.get(platform_name)
        if not cls:
            print(f"[!] Unknown platform: {platform_name}")
            continue

        print(f"\n── Scraping {platform_name.upper()} ──")
        scraper = cls(credentials=build_credentials(platform_name))
        scraper.login()
        channels = scraper.get_channels()
        all_channels.extend(channels)

    if not all_channels:
        print("\nNo channels found.")
        return

    print(f"\n✅ Total channels collected: {len(all_channels)}")

    if fmt in ("m3u", "both"):
        m3u_path = output if (output and output.endswith(".m3u")) else "output/playlist.m3u"
        export_m3u(all_channels, m3u_path)

    if fmt in ("json", "both"):
        json_path = output if (output and output.endswith(".json")) else "output/channels.json"
        export_json(all_channels, json_path)


def main():
    parser = argparse.ArgumentParser(
        description="🇵🇰 Pakistani OTT Live Channel Scraper"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true", help="Scrape all supported platforms")
    group.add_argument("--platform", choices=list(PLATFORM_MAP.keys()), help="Scrape a specific platform")

    parser.add_argument("--format", choices=["m3u", "json", "both"], default="both",
                        help="Output format (default: both)")
    parser.add_argument("--output", type=str, help="Custom output file path")

    args = parser.parse_args()

    platforms = list(PLATFORM_MAP.keys()) if args.all else [args.platform]
    run(platforms, args.format, args.output)


if __name__ == "__main__":
    main()
