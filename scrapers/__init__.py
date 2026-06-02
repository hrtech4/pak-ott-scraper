from scrapers.tamasha import TamashaScaper
from scrapers.tapmad import TapmadScraper
from scrapers.myco import MyCoScraper

PLATFORM_MAP = {
    "tamasha": TamashaScaper,
    "tapmad": TapmadScraper,
    "myco": MyCoScraper,
}

__all__ = ["TamashaScaper", "TapmadScraper", "MyCoScraper", "PLATFORM_MAP"]
