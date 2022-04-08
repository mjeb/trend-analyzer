import logging
from dateutil import parser

import requests
import emporium
from emporium import Store
import pandas as pd
from bs4 import BeautifulSoup


from domain.search_service import SearchService

log = logging.getLogger(__name__)


_COLUMNS = ["date", "title", "link", "creator"]


class ZorgvisieSearchService(SearchService):
    """Queries zorgvisie.nl website for articles regarding a certain content"""

    def __init__(self, url: str, store: Store):
        self._url = url
        self._store = store

    def search(self, _query=None, _query_config=None):
        log.info("...Fetching Zorgvisie news articles links from rss feed")
        html = requests.get(self._url, timeout=30)
        soup = BeautifulSoup(html.text, features="xml")
        articles = []
        items = [item for item in soup.find_all("item")]
        for item in items:
            log.info(item)
            title = item.find('title').text
            link = item.find('link').text
            published = parser.parse(item.find('pubDate').text).date()
            creator = item.find("dc:creator").text
            article = {
                'title': title,
                'link': link,
                'date': published,
                "creator": creator,
            }
            articles.append(article)
        results = pd.DataFrame(articles)[_COLUMNS]
        self._write_to_store(results)
        return results["link"].values.tolist()

    def _write_to_store(self, results: pd.DataFrame):
        cached_results = self._read_cache()
        updated_results = pd.concat((cached_results, results)).drop_duplicates(subset=["link"], keep="first")
        with self._store.write("cached_article_links.csv", "b", encoding="utf-8") as h:
            updated_results.to_csv(h, line_terminator="\r", encoding="utf-8")

    def _read_cache(self) -> pd.DataFrame:
        try:
            with self._store.open("cached_article_links.csv", "r") as h:
                return pd.read_csv(h, index_col=0)
        except emporium.base.NoSuchFile:
            return pd.DataFrame(columns=_COLUMNS)
