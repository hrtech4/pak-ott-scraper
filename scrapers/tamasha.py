"""
tamasha.py — Scraper for Tamasha.tv live channels.

Tamasha loads channel data via a REST API after initial page load.
We intercept the API endpoint to get stream tokens directly.

Reverse-engineered endpoints (may change):
  - Channel list: GET https://tamasha.tv/api/v2/livetv/channels
  - Stream URL:   POST https://tamasha.tv/api/v2/livetv/stream/{channel_slug}
"""

import requests
from scrapers.base import BaseScraper, Channel


class TamashaScaper(BaseScraper):

    PLATFORM_NAME = "tamasha"
    BASE_URL = "https://tamasha.tv"
    API_BASE = "https://tamasha.tv/api/v2"

    CHANNEL_LIST_URL = f"{API_BASE}/livetv/channels"
    STREAM_URL_TEMPLATE = f"{API_BASE}/livetv/stream/{{slug}}"

    def __init__(self, credentials=None, timeout=15):
        super().__init__(credentials, timeout)
        self.session = requests.Session()
        self.session.headers.update(self._build_headers())

    def _build_headers(self) -> dict:
        headers = super()._build_headers()
        headers.update({
            "Origin": self.BASE_URL,
            "X-Requested-With": "XMLHttpRequest",
        })
        return headers

    def get_channels(self) -> list[Channel]:
        """Fetch channel list and resolve each stream URL."""
        channels = []

        try:
            resp = self.session.get(self.CHANNEL_LIST_URL, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"[Tamasha] Failed to fetch channel list: {e}")
            return channels

        # Adjust key names based on actual API response shape
        channel_list = data.get("data", data.get("channels", []))

        for item in channel_list:
            slug = item.get("slug") or item.get("id")
            name = item.get("title") or item.get("name", "Unknown")
            logo = item.get("logo") or item.get("thumbnail")
            category = item.get("category", {}).get("name", "General") \
                        if isinstance(item.get("category"), dict) \
                        else item.get("category", "General")

            stream_url = self._get_stream_url(slug)
            if not stream_url:
                print(f"[Tamasha] Skipping '{name}' — no stream URL")
                continue

            channels.append(Channel(
                id=f"tamasha-{slug}",
                name=name,
                platform=self.PLATFORM_NAME,
                stream_url=stream_url,
                category=category,
                logo=logo,
            ))

        print(f"[Tamasha] Found {len(channels)} channels")
        return channels

    def _get_stream_url(self, slug: str) -> str | None:
        """Request a playback URL for a specific channel slug."""
        url = self.STREAM_URL_TEMPLATE.format(slug=slug)
        try:
            resp = self.session.post(url, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            # Common response keys — adjust to actual API
            return (
                data.get("stream_url")
                or data.get("url")
                or data.get("hls_url")
                or data.get("data", {}).get("stream_url")
            )
        except Exception as e:
            print(f"[Tamasha] Stream URL error for '{slug}': {e}")
            return None
