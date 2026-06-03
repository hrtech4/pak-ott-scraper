"""
Tamasha.tv Live Channel Scraper
Targets the web app's channel/stream API endpoints.
"""

import re
import aiohttp
from .base import BaseScraper


class TamashaScraer(BaseScraper):
    name = "Tamasha"

    # Tamasha loads channels via its API; these are the known endpoints.
    BASE_URL   = "https://tamasha.tv"
    API_BASE   = "https://tamasha.tv/api/v2"
    HEADERS    = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer":    "https://tamasha.tv/live-tv",
        "Origin":     "https://tamasha.tv",
    }

    async def scrape(self):
        channels = []

        async with aiohttp.ClientSession(headers=self.HEADERS) as session:
            # Step 1: get channel list
            list_url = f"{self.API_BASE}/channels?type=live&limit=200&page=1"
            data = await self.get_json(session, list_url)
            if not data:
                self.logger.warning("Tamasha: channel list empty / blocked")
                return channels

            items = (
                data.get("data", {}).get("channels")
                or data.get("channels")
                or data.get("data", [])
                or []
            )

            for item in items:
                ch = await self._parse_channel(session, item)
                if ch:
                    channels.append(ch)

        return channels

    async def _parse_channel(self, session, item):
        try:
            ch_id   = item.get("id") or item.get("slug")
            name    = item.get("title") or item.get("name", "Unknown")
            logo    = item.get("logo") or item.get("thumbnail") or item.get("image", "")
            group   = item.get("category") or item.get("genre", "General")

            # Fetch stream URL
            stream_url = f"{self.API_BASE}/channels/{ch_id}/stream"
            stream_data = await self.get_json(session, stream_url)
            if not stream_data:
                return None

            url = (
                stream_data.get("url")
                or stream_data.get("stream_url")
                or stream_data.get("data", {}).get("url")
            )
            if not url or not url.startswith("http"):
                return None

            return self.build_channel(
                name=name,
                url=url,
                logo=self.ensure_abs(logo),
                group=group,
                source=self.name,
            )
        except Exception as e:
            self.logger.debug(f"Tamasha parse error: {e}")
            return None

    def ensure_abs(self, url):
        if url and url.startswith("/"):
            return self.BASE_URL + url
        return url or ""
