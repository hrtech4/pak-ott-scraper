"""
tapmad.py — Scraper for Tapmad.com live channels.

Tapmad uses a token-based auth system. Free tier channels are accessible
without login; premium channels require a valid session token.

Observed endpoints:
  - Channel list: GET https://tapmad.com/api/channels/live
  - Stream token: GET https://tapmad.com/api/stream/token?channel={id}
"""

import requests
from scrapers.base import BaseScraper, Channel


class TapmadScraper(BaseScraper):

    PLATFORM_NAME = "tapmad"
    BASE_URL = "https://tapmad.com"
    API_BASE = "https://tapmad.com/api"

    CHANNEL_LIST_URL = f"{API_BASE}/channels/live"
    STREAM_TOKEN_URL = f"{API_BASE}/stream/token"

    def __init__(self, credentials=None, timeout=15):
        super().__init__(credentials, timeout)
        self.session = requests.Session()
        self.session.headers.update(self._build_headers())
        self._auth_token: str | None = None

    def _build_headers(self) -> dict:
        headers = super()._build_headers()
        headers.update({
            "Origin": self.BASE_URL,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        })
        return headers

    def login(self) -> bool:
        """
        Authenticate with Tapmad using email/password credentials.
        Sets self._auth_token on success.
        """
        email = self.credentials.get("email")
        password = self.credentials.get("password")
        if not email or not password:
            print("[Tapmad] No credentials supplied; using anonymous mode.")
            return False

        login_url = f"{self.API_BASE}/user/login"
        try:
            resp = self.session.post(login_url, json={
                "email": email,
                "password": password,
            }, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            token = data.get("token") or data.get("access_token")
            if token:
                self._auth_token = token
                self.session.headers["Authorization"] = f"Bearer {token}"
                print("[Tapmad] Login successful.")
                return True
        except Exception as e:
            print(f"[Tapmad] Login failed: {e}")
        return False

    def get_channels(self) -> list[Channel]:
        channels = []

        try:
            resp = self.session.get(self.CHANNEL_LIST_URL, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"[Tapmad] Failed to fetch channels: {e}")
            return channels

        channel_list = data.get("channels") or data.get("data") or []

        for item in channel_list:
            ch_id = item.get("id") or item.get("channel_id")
            name = item.get("name") or item.get("title", "Unknown")
            logo = item.get("logo") or item.get("icon")
            category = item.get("genre") or item.get("category", "General")
            is_premium = item.get("premium", False)

            # Skip premium channels if not authenticated
            if is_premium and not self._auth_token:
                print(f"[Tapmad] Skipping premium channel '{name}' (not logged in)")
                continue

            stream_url = self._get_stream_url(ch_id)
            if not stream_url:
                continue

            channels.append(Channel(
                id=f"tapmad-{ch_id}",
                name=name,
                platform=self.PLATFORM_NAME,
                stream_url=stream_url,
                category=category,
                logo=logo,
            ))

        print(f"[Tapmad] Found {len(channels)} channels")
        return channels

    def _get_stream_url(self, channel_id) -> str | None:
        try:
            resp = self.session.get(
                self.STREAM_TOKEN_URL,
                params={"channel": channel_id},
                timeout=self.timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            return (
                data.get("stream_url")
                or data.get("url")
                or data.get("hls")
                or data.get("data", {}).get("url")
            )
        except Exception as e:
            print(f"[Tapmad] Stream error for channel {channel_id}: {e}")
            return None
