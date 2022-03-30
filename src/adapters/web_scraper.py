import re
import logging
from typing import List
from hashlib import sha256

import requests
from emporium import Store
from bs4 import BeautifulSoup


log = logging.getLogger(__name__)


class WebScraper:
    def __init__(self, store: Store):
        self._store = store

    def fetch_text(self, link: str) -> List[str]:
        text = self._fetch_from_cache(link)
        if not text:
            text = self._fetch_and_cache(link)
        return text

    def _fetch_from_cache(self, link: str) -> List[str]:
        try:
            encoded_link = sha256(link.encode("utf-8")).hexdigest()
            cached_links = [l.entry for l in self._store.list()]
            if encoded_link in cached_links:
                log.info("...Fetching from cache: %s", link)
                substore = self._store.substore(encoded_link)
                with substore.open("web_text.txt", "r", encoding='utf8') as h:
                    return h.read()
            return []
        except FileNotFoundError:
            return []

    def _fetch_and_cache(self, link: str) -> str:
        log.info("...Scraping: %s", link)
        hashed_link = sha256(link.encode("utf-8")).hexdigest()
        html = requests.get(link).text
        soup = BeautifulSoup(html, "html.parser")
        text = "\n".join([x.text for x in soup.find_all("p")])
        cleaned = _clean_text(text)
        substore = self._store.substore(hashed_link)
        with substore.open("web_text.txt", "w+", encoding='utf8') as h:
            h.write(cleaned)
        return cleaned


def _clean_text(text: str) -> str:
    cleaned = text.replace("  ", " ")
    cleaned = re.sub("\[\d+\]", "", cleaned)
    cleaned = re.sub("\d+. ", "", cleaned)
    return cleaned.replace("\n\n", "\n")
