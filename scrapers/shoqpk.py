"""
ShoqPK (shoq.pk) Live Channel Scraper
"""

import re
import aiohttp
from bs4 import BeautifulSoup
from .base import BaseScraper


class ShoqPKScraper(BaseScraper):
    name = "ShoqPK"

    BASE_URL = "https://shoq.pk"
    HEADERS  = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer":    "https://shoq.pk/live",
    }

    # Regex patterns to extract HLS streams from JS bundles / page source
    HLS_PATTERNS = [
        re.compile(r"['\"]?(https?://[^'\"]+\.m3u8[^'\"]*)['\"]?"),
        re.compile(r"source\s*:\s*['\"]?(https?://[^'\"]+\.m3u8[^'\"]*)['\"]?"),
        re.compile(r"file\s*:\s*['\"]?(https?://[^'\"]+\.m3u8[^'\"]*)['\"]?"),
    ]

    async def scrape(self):
        channels = []
        async with aiohttp.ClientSession(headers=self.HEADERS) as session:
            # Try JSON API first
            api_channels = await self._try_api(session)
            if api_channels:
                return api_channels

            # Fallback: scrape HTML page
            html = await self.get_text(session, f"{self.BASE_URL}/live")
            if not html:
                return channels

            soup = BeautifulSoup(html, "html.parser")
            channel_links = soup.select("a[href*='/channel/'], a[href*='/live/']")

            for link in channel_links[:50]:  # cap at 50
                href = link.get("href", "")
                if not href:
                    continue
                full_url = href if href.startswith("http") else self.BASE_URL + href
                ch = await self._scrape_channel_page(session, full_url, link)
                if ch:
                    channels.append(ch)

        return channels

    async def _try_api(self, session):
        """Try known API endpoints before falling back to HTML scraping."""
        for endpoint in ["/api/channels", "/api/live", "/api/v1/channels"]:
            data = await self.get_json(session, self.BASE_URL + endpoint)
            if data:
                items = data.get("channels") or data.get("data") or []
                result = []
                for item in items:
                    url = item.get("stream_url") or item.get("url") or item.get("hls")
                    if url and url.startswith("http"):
                        result.append(self.build_channel(
                            name=item.get("name", "Unknown"),
                            url=url,
                            logo=item.get("logo", ""),
                            group=item.get("category", "General"),
                            source=self.name,
                        ))
                if result:
                    return result
        return None

    async def _scrape_channel_page(self, session, page_url, link_el):
        """Fetch a channel detail page and extract the HLS stream URL."""
        try:
            name = (
                link_el.get_text(strip=True)
                or link_el.find("img", alt=True) and link_el.find("img")["alt"]
                or "Unknown"
            )
            logo_tag = link_el.find("img")
            logo = logo_tag.get("src", "") if logo_tag else ""
            if logo and not logo.startswith("http"):
                logo = self.BASE_URL + logo

            page_html = await self.get_text(session, page_url)
            if not page_html:
                return None

            for pat in self.HLS_PATTERNS:
                m = pat.search(page_html)
                if m:
                    stream_url = m.group(1)
                    return self.build_channel(
                        name=name,
                        url=stream_url,
                        logo=logo,
                        group="General",
                        source=self.name,
                    )
        except Exception as e:
            self.logger.debug(f"ShoqPK page error: {e}")
        return None
