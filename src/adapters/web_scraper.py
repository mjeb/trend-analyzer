import re
import logging
import requests
from hashlib import sha256

from emporium import Store
from bs4 import BeautifulSoup


log = logging.getLogger(__name__)


class WebScraper:

    def __init__(self, store: Store):
        self._store = store

    def fetch_text(self, link: str) -> str:
        log.info("...Scraping: %s", link)
        html = requests.get(link, timeout=30)
        soup = BeautifulSoup(html.text, "html.parser")
        text = "\n".join([x.text for x in soup.find_all("p")])
        cleaned = self._clean_text(text)
        self._to_cache(cleaned, link)
        return cleaned

    @staticmethod
    def _clean_text(text: str) -> str:
        cleaned = text.replace("  ", " ")
        cleaned = re.sub("\[\d+\]", "", cleaned)
        cleaned = re.sub("\d+. ", "", cleaned)
        return cleaned.replace("\n\n", "\n")

    def _to_cache(self, text: str, link: str):
        hashed_link = sha256(link.encode("utf-8")).hexdigest()
        substore = self._store.substore(hashed_link)
        with substore.open("web_text.txt", "w+", encoding='utf8') as h:
            h.write(text)
