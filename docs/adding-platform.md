# Adding a New Platform

Follow these steps to add support for a new Pakistani OTT platform.

## 1. Reverse-engineer the stream API

Open the platform's website in Chrome, go to **DevTools → Network tab**, filter by `XHR` or `Fetch`, then navigate to the live TV section. Look for:

- A channel listing endpoint (usually returns JSON with channel names, slugs, logos)
- A stream URL endpoint (returns an HLS `.m3u8` or DASH `.mpd` URL)

Note the full URL, any required headers (`Authorization`, `x-api-key`, etc.), and request method (GET / POST).

## 2. Create the scraper file

```bash
touch scrapers/newplatform.py
```

Minimal template:

```python
import requests
from scrapers.base import BaseScraper, Channel

class NewPlatformScraper(BaseScraper):

    PLATFORM_NAME = "newplatform"
    BASE_URL = "https://newplatform.pk"

    def __init__(self, credentials=None, timeout=15):
        super().__init__(credentials, timeout)
        self.session = requests.Session()
        self.session.headers.update(self._build_headers())

    def get_channels(self) -> list[Channel]:
        # TODO: implement
        return []
```

## 3. Register it

In `scrapers/__init__.py`:

```python
from scrapers.newplatform import NewPlatformScraper

PLATFORM_MAP = {
    ...
    "newplatform": NewPlatformScraper,
}
```

## 4. Test it

```bash
python main.py --platform newplatform --format json
cat output/channels.json
```

## 5. Add docs

Create `docs/newplatform.md` with:
- Base URL and discovered API endpoints
- Auth requirements
- Any DRM notes
- Known issues / stream expiry time
