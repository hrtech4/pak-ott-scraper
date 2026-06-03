"""
Tapmad.com Live Channel Scraper
"""

import aiohttp
from .base import BaseScraper


class TapmadScraper(BaseScraper):
    name = "Tapmad"

    API_BASE = "https://cdn.tapmad.com/api/v1"
    HEADERS  = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 Chrome/120",
        "Referer":    "https://tapmad.com/",
        "Origin":     "https://tapmad.com",
    }

    async def scrape(self):
        channels = []
        async with aiohttp.ClientSession(headers=self.HEADERS) as session:
            data = await self.get_json(session, f"{self.API_BASE}/channels/live")
            if not data:
                self.logger.warning("Tapmad: no data returned")
                return channels

            items = (
                data.get("channels")
                or data.get("data")
                or data.get("result", [])
            )

            for item in items:
                ch = self._parse(item)
                if ch:
                    channels.append(ch)

        return channels

    def _parse(self, item):
        try:
            name  = item.get("title") or item.get("name", "Unknown")
            logo  = item.get("logo") or item.get("icon") or item.get("image", "")
            group = item.get("genre") or item.get("category", "General")
            url   = (
                item.get("stream_url")
                or item.get("url")
                or item.get("hls_url")
                or item.get("streamUrl", "")
            )
            if not url or not url.startswith("http"):
                return None
            return self.build_channel(
                name=name, url=url, logo=logo, group=group, source=self.name
            )
        except Exception as e:
            self.logger.debug(f"Tapmad parse error: {e}")
            return None
