# config.py — Global configuration for pak-ott-scraper

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

REQUEST_TIMEOUT = 15        # seconds per HTTP request
RETRY_ATTEMPTS = 3          # retries on failure
STREAM_REFRESH_INTERVAL = 3600  # re-scrape every hour (streams expire)
OUTPUT_DIR = "output"
