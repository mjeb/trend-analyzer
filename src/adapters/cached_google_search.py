import logging
import datetime as dt
from typing import Dict, List, Union

import emporium.base
import pandas as pd
from emporium import Store
from googleapiclient.discovery import build

from adapters.google_search import GoogleQueryService


log = logging.getLogger(__name__)

SearchResult = Dict[str, Union[str, Dict]]
SearchResults = List[SearchResult]

_COLUMNS = ["date", "query", "cx", "start", "num", "title", "snippet", "link"]


class CachedGoogleQueryService:
    """ "Uses Google custom search API find search results for topics/queries"""

    def __init__(self, service, store: Store):
        self._service = service
        self._store = store

    @classmethod
    def from_config(cls, config: Dict):
        dev_key = config.get("developer_key")
        store = config.get("store")
        api_service = build("customsearch", "v1", developerKey=dev_key)
        service = GoogleQueryService(api_service)
        return cls(service, store)

    def search(self, query, query_config: Dict) -> pd.DataFrame:
        # config needs to contain cx (cse_id) and num parameters
        log.info("...Searching search results for %s", query)
        results = self._fetch_from_store(query, query_config)
        if results.empty:
            log.info("...No cached results found, querying Google")
            results = self._service.search(query, query_config)
            self._write_to_store(results)
        return results["link"].values.tolist()

    def _fetch_from_store(self, query, query_config) -> pd.DataFrame:
        """Checks if query has been done recently and if so, fetches these results. This
        to prevent over-usage of the API, which is limited to 100 requests per day"""
        log.info("...Search in recent cached results")
        today = dt.date.today()
        cached_results = self._read_cache()
        cached_results["date"] = pd.to_datetime(cached_results["date"], infer_datetime_format=True).dt.date
        mask_query = cached_results["query"] == query
        mask_cx = cached_results["cx"] == query_config.get("cx")
        mask_start = cached_results["start"] == query_config.get("start")
        mask_num = cached_results["num"] == query_config.get("num")
        mask_date = cached_results["date"] >= today - dt.timedelta(days=28)
        return cached_results[mask_query & mask_cx & mask_start & mask_num & mask_date]

    def _read_cache(self) -> pd.DataFrame:
        try:
            with self._store.open("cached_search_results.csv", "r") as h:
                return pd.read_csv(h, index_col=0)
        except emporium.base.NoSuchFile:
            return pd.DataFrame(columns=_COLUMNS)

    def _write_to_store(self, results: pd.DataFrame):
        cached_results = self._read_cache()
        updated_results = pd.concat((cached_results, results))
        with self._store.write("cached_search_results.csv", "b", encoding="utf-8") as h:
            updated_results.to_csv(h, line_terminator="\r", encoding="utf-8")
