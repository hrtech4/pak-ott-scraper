"""
base.py — Abstract base class for all OTT platform scrapers.
All platform scrapers must extend this class.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Channel:
    """Represents a single live TV channel."""
    id: str
    name: str
    platform: str
    stream_url: str
    category: str = "General"
    logo: Optional[str] = None
    drm: bool = False
    drm_key: Optional[str] = None
    language: str = "ur"
    country: str = "PK"
    refreshed_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "platform": self.platform,
            "category": self.category,
            "logo": self.logo,
            "stream_url": self.stream_url,
            "drm": self.drm,
            "drm_key": self.drm_key,
            "language": self.language,
            "country": self.country,
            "refreshed_at": self.refreshed_at,
        }

    def to_m3u_entry(self) -> str:
        logo_attr = f' tvg-logo="{self.logo}"' if self.logo else ""
        return (
            f'#EXTINF:-1 tvg-id="{self.id}" tvg-name="{self.name}"'
            f'{logo_attr} group-title="{self.category}",{self.name}\n'
            f'{self.stream_url}\n'
        )


class BaseScraper(ABC):
    """
    Abstract base scraper. All platform scrapers must implement:
      - get_channels() -> list[Channel]
    Optionally override:
      - login()        for authenticated sessions
      - refresh()      if stream URLs expire and need re-fetching
    """

    PLATFORM_NAME: str = "unknown"
    BASE_URL: str = ""

    def __init__(self, credentials: Optional[dict] = None, timeout: int = 15):
        self.credentials = credentials or {}
        self.timeout = timeout
        self.session = None  # requests.Session() set in subclass
        self._channels: list[Channel] = []

    @abstractmethod
    def get_channels(self) -> list[Channel]:
        """
        Fetch all available live channels from the platform.
        Returns a list of Channel objects.
        """
        ...

    def login(self) -> bool:
        """
        Authenticate with the platform (optional).
        Returns True on success, False otherwise.
        Override in subclass if login is required.
        """
        return True

    def refresh(self) -> list[Channel]:
        """Re-fetch channels (stream URLs often expire). Calls get_channels() by default."""
        self._channels = self.get_channels()
        return self._channels

    def _build_headers(self) -> dict:
        """Return common HTTP headers. Override to customise per platform."""
        from config import USER_AGENT
        return {
            "User-Agent": USER_AGENT,
            "Accept": "application/json, text/html, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": self.BASE_URL,
        }

    def __repr__(self):
        return f"<{self.__class__.__name__} platform={self.PLATFORM_NAME}>"
