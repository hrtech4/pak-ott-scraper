"""
MyCo (myco.io) Live Channel Scraper
"""

import aiohttp
from .base import BaseScraper


class MyCoScraper(BaseScraper):
    name = "MyCo"

    API_BASE = "https://api.myco.io/v1"
    HEADERS  = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer":    "https://myco.io/",
        "Origin":     "https://myco.io",
        "Accept":     "application/json",
    }

    async def scrape(self):
        channels = []
        async with aiohttp.ClientSession(headers=self.HEADERS) as session:
            # MyCo uses paginated listings
            page = 1
            while True:
                url = f"{self.API_BASE}/live-channels?page={page}&per_page=50"
                data = await self.get_json(session, url)
                if not data:
                    break

                items = data.get("data") or data.get("channels") or []
                if not items:
                    break

                for item in items:
                    ch = await self._parse(session, item)
                    if ch:
                        channels.append(ch)

                # Check if there are more pages
                total_pages = (
                    data.get("meta", {}).get("last_page")
                    or data.get("last_page")
                    or 1
                )
                if page >= total_pages:
                    break
                page += 1

        return channels

    async def _parse(self, session, item):
        try:
            name    = item.get("name") or item.get("title", "Unknown")
            logo    = item.get("logo") or item.get("thumbnail", "")
            group   = item.get("category") or item.get("genre", "General")
            channel_id = item.get("id") or item.get("slug")

            # Try direct URL first
            url = item.get("stream_url") or item.get("hls_url") or item.get("url")

            # If not embedded, hit the stream endpoint
            if not url and channel_id:
                stream_data = await self.get_json(
                    session, f"{self.API_BASE}/channels/{channel_id}/stream"
                )
                if stream_data:
                    url = stream_data.get("url") or stream_data.get("stream_url")

            if not url or not url.startswith("http"):
                return None

            return self.build_channel(
                name=name, url=url, logo=logo, group=group, source=self.name
            )
        except Exception as e:
            self.logger.debug(f"MyCo parse error: {e}")
            return None
