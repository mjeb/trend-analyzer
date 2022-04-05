import logging
import datetime as dt
from typing import Dict, List, Union

import emporium.base
import pandas as pd
from emporium import Store
from googleapiclient.discovery import build


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
        service = build("customsearch", "v1", developerKey=dev_key)
        return cls(service, store)

    def search(self, query, query_config: Dict) -> pd.DataFrame:
        # config needs to contain cx (cse_id) and num parameters
        log.info("...Searching search results for %s", query)
        results = self._fetch_from_cache(query, query_config)
        if results.empty:
            log.info("...No cached results found, querying Google")
            results = self._service.search(query, query_config)
        return results

    def _fetch_from_cache(self, query, query_config) -> pd.DataFrame:
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


def _to_result_format(raw_results: SearchResults, query, query_config) -> pd.DataFrame:
    results = []
    for result in raw_results:
        row = dict()
        for element in ("title", "snippet", "link"):
            row[element] = result.get(element)
        results.append(row)
    data = pd.DataFrame(results)
    data["date"] = dt.date.today().strftime("%Y-%m-%d")
    data["query"] = query
    data["cx"] = query_config.get("cx")
    data["start"] = query_config.get("start")
    data["num"] = query_config.get("num")
    return data
