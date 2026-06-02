"""
myco.py — Scraper for MyCo (myco.com.pk) live channels.

MyCo renders its channel grid via React; channel data is injected into
the page as a __NEXT_DATA__ JSON blob or fetched via an internal API.

Strategy:
  1. Try the internal API endpoint first (fast path).
  2. Fall back to parsing __NEXT_DATA__ from the HTML (slower but robust).
"""

import json
import re
import requests
from scrapers.base import BaseScraper, Channel


class MyCoScraper(BaseScraper):

    PLATFORM_NAME = "myco"
    BASE_URL = "https://myco.com.pk"
    LIVE_PAGE_URL = f"{BASE_URL}/live"
    API_BASE = f"{BASE_URL}/api"  # adjust when discovered

    def __init__(self, credentials=None, timeout=15):
        super().__init__(credentials, timeout)
        self.session = requests.Session()
        self.session.headers.update(self._build_headers())

    def _build_headers(self) -> dict:
        headers = super()._build_headers()
        headers.update({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })
        return headers

    def get_channels(self) -> list[Channel]:
        """Try API first, fall back to page scrape."""
        channels = self._try_api()
        if not channels:
            print("[MyCo] API path failed, trying page scrape...")
            channels = self._scrape_next_data()
        print(f"[MyCo] Found {len(channels)} channels")
        return channels

    # ── Fast path: internal JSON API ────────────────────────────────────────

    def _try_api(self) -> list[Channel]:
        """
        Attempt to call the undocumented internal API.
        Update the URL once discovered via browser DevTools → Network tab.
        """
        api_url = f"{self.API_BASE}/livetv/channels"  # placeholder
        try:
            resp = self.session.get(api_url, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            return self._parse_api_response(data)
        except Exception:
            return []

    def _parse_api_response(self, data: dict | list) -> list[Channel]:
        channels = []
        items = data if isinstance(data, list) else data.get("channels", data.get("data", []))
        for item in items:
            ch = self._item_to_channel(item)
            if ch:
                channels.append(ch)
        return channels

    # ── Fallback: parse __NEXT_DATA__ from HTML ──────────────────────────────

    def _scrape_next_data(self) -> list[Channel]:
        try:
            resp = self.session.get(self.LIVE_PAGE_URL, timeout=self.timeout)
            resp.raise_for_status()
            html = resp.text
        except Exception as e:
            print(f"[MyCo] Failed to load live page: {e}")
            return []

        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)
        if not match:
            print("[MyCo] __NEXT_DATA__ not found in page HTML.")
            return []

        try:
            next_data = json.loads(match.group(1))
        except json.JSONDecodeError as e:
            print(f"[MyCo] JSON parse error: {e}")
            return []

        # Navigate the Next.js page props — adjust path per actual data shape
        props = next_data.get("props", {}).get("pageProps", {})
        items = (
            props.get("channels")
            or props.get("liveChannels")
            or props.get("data", {}).get("channels", [])
        )

        channels = []
        for item in items:
            ch = self._item_to_channel(item)
            if ch:
                channels.append(ch)
        return channels

    # ── Shared item → Channel mapper ─────────────────────────────────────────

    def _item_to_channel(self, item: dict) -> Channel | None:
        ch_id = item.get("id") or item.get("slug") or item.get("channel_id")
        name = item.get("name") or item.get("title")
        stream_url = (
            item.get("stream_url")
            or item.get("hls_url")
            or item.get("url")
            or item.get("playback_url")
        )

        if not ch_id or not name or not stream_url:
            return None

        return Channel(
            id=f"myco-{ch_id}",
            name=name,
            platform=self.PLATFORM_NAME,
            stream_url=stream_url,
            category=item.get("category", "General"),
            logo=item.get("logo") or item.get("thumbnail"),
        )
