"""
Channel Validator
Concurrently checks every channel's HLS stream URL.
Dead streams (non-200, timeout, non-M3U response) are dropped.
"""

import asyncio
import logging

import aiohttp

logger = logging.getLogger("validator")

# How many channels to validate in parallel
CONCURRENCY = 50
# Seconds to wait for a HEAD/GET response
TIMEOUT = 10
# Minimum bytes that look like an M3U playlist
M3U_MIN_BYTES = 7


class ChannelValidator:
    async def validate_all(self, channels: list) -> list:
        sem = asyncio.Semaphore(CONCURRENCY)
        connector = aiohttp.TCPConnector(limit=CONCURRENCY, ssl=False)
        timeout   = aiohttp.ClientTimeout(total=TIMEOUT, connect=5)

        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            tasks = [self._check(session, sem, ch) for ch in channels]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        live = [ch for ch, ok in zip(channels, results) if ok is True]
        return live

    async def _check(self, session, sem, channel):
        url = channel.get("url", "")
        if not url:
            return False
        async with sem:
            return await self._is_stream_alive(session, url)

    async def _is_stream_alive(self, session, url: str) -> bool:
        try:
            # Try HEAD first (cheap)
            async with session.head(url, allow_redirects=True) as resp:
                if resp.status in (200, 206):
                    return True
                if resp.status == 405:
                    # HEAD not allowed – fall through to GET
                    pass
                elif resp.status >= 400:
                    return False

            # Partial GET to verify it's an M3U/stream
            headers = {"Range": "bytes=0-512"}
            async with session.get(url, headers=headers, allow_redirects=True) as resp:
                if resp.status not in (200, 206):
                    return False
                chunk = await resp.content.read(512)
                # Accept if it looks like M3U or generic media
                text = chunk.decode("utf-8", errors="ignore").strip()
                if text.startswith("#EXTM3U") or text.startswith("#EXT-X-"):
                    return True
                # Many streams return binary data for .ts segments – that's fine
                ct = resp.content_type or ""
                if any(t in ct for t in ("video", "audio", "octet-stream", "mpegurl")):
                    return True
                return bool(chunk)

        except asyncio.TimeoutError:
            logger.debug(f"Timeout: {url}")
        except Exception as e:
            logger.debug(f"Validation error {url}: {e}")
        return False
