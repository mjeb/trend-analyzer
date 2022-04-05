import logging
from typing import List
from hashlib import sha256

from emporium import Store

from utils.time_out_exception import TimeoutError

log = logging.getLogger(__name__)


class CachedWebScraper:
    """Uses the cached text if available else uses the web scraper"""

    def __init__(self, scraper, store: Store):
        self._scraper = scraper
        self._store = store

    def fetch_text(self, link: str) -> List[str]:
        text = self._fetch_from_cache(link)
        if not text:
            text = self._scraper.fetch_text(link)
            self._to_cache(text, link)
        return text

    def _fetch_from_cache(self, link: str) -> List[str]:
        try:
            cached_links = [l.entry for l in self._store.list()]
            self._from_cache(link, cached_links)
        except FileNotFoundError:
            return []

    def _from_cache(self, link: str, cached_links: List[str]) -> List[str]:
        try:
            encoded_link = sha256(link.encode("utf-8")).hexdigest()
        except AttributeError:
            import pdb
            pdb.set_trace()
        if not encoded_link in cached_links:
            return []
        log.info("...Fetching from cache: %s", link)
        substore = self._store.substore(encoded_link)
        with substore.open("web_text.txt", "r", encoding='utf8') as h:
            return h.read()

    def _to_cache(self, text: str, link: str):
        hashed_link = sha256(link.encode("utf-8")).hexdigest()
        substore = self._store.substore(hashed_link)
        with substore.open("web_text.txt", "w+", encoding='utf8') as h:
            h.write(text)
