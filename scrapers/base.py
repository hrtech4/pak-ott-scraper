"""
Base class for all OTT scrapers.
"""

import asyncio
import logging
from typing import Optional


class BaseScraper:
    name: str = "Base"
    TIMEOUT: int = 20  # seconds per request

    def __init__(self):
        self.logger = logging.getLogger(f"scraper.{self.name.lower()}")

    async def get_json(self, session, url: str, **kwargs) -> Optional[dict]:
        try:
            async with session.get(url, timeout=self.TIMEOUT, **kwargs) as resp:
                if resp.status == 200:
                    return await resp.json(content_type=None)
                self.logger.debug(f"GET {url} → HTTP {resp.status}")
        except asyncio.TimeoutError:
            self.logger.debug(f"Timeout: {url}")
        except Exception as e:
            self.logger.debug(f"JSON error {url}: {e}")
        return None

    async def get_text(self, session, url: str, **kwargs) -> Optional[str]:
        try:
            async with session.get(url, timeout=self.TIMEOUT, **kwargs) as resp:
                if resp.status == 200:
                    return await resp.text()
                self.logger.debug(f"GET {url} → HTTP {resp.status}")
        except asyncio.TimeoutError:
            self.logger.debug(f"Timeout: {url}")
        except Exception as e:
            self.logger.debug(f"Text error {url}: {e}")
        return None

    def build_channel(
        self,
        name: str,
        url: str,
        logo: str = "",
        group: str = "General",
        source: str = "",
        country: str = "PK",
        language: str = "Urdu",
    ) -> dict:
        return {
            "name":     name.strip(),
            "url":      url.strip(),
            "logo":     logo.strip(),
            "group":    group.strip() or "General",
            "source":   source or self.name,
            "country":  country,
            "language": language,
        }

    async def scrape(self) -> list:
        raise NotImplementedError
