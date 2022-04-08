import re
import logging

import requests
from bs4 import BeautifulSoup


log = logging.getLogger(__name__)


class WebScraper:
    """Simple tool to extract and slightly clean up text from web pages"""

    def fetch_text(self, link: str) -> str:
        log.info("...Scraping: %s", link)
        html = requests.get(link, timeout=30)
        soup = BeautifulSoup(html.text, "html.parser")
        text = "\n".join([x.text for x in soup.find_all("p")])
        return self._clean_text(text)

    @staticmethod
    def _clean_text(text: str) -> str:
        cleaned = text.replace("  ", " ")
        cleaned = re.sub("\[\d+\]", "", cleaned)
        cleaned = re.sub("\d+. ", "", cleaned)
        return cleaned.replace("\n\n", "\n")
