import logging
import datetime as dt
from typing import Dict, List, Union

import pandas as pd

from domain.search_service import SearchService

log = logging.getLogger(__name__)

SearchResult = Dict[str, Union[str, Dict]]
SearchResults = List[SearchResult]

_COLUMNS = ["date", "query", "cx", "start", "num", "title", "snippet", "link"]


class GoogleQueryService(SearchService):
    """ "Uses Google custom search API find search results for topics/queries"""

    def __init__(self, service):
        self._service = service

    def search(self, query, query_config: Dict) -> pd.DataFrame:
        # config needs to contain cx (cse_id) and num parameters
        log.info("...Searching search results for: %s", query)
        raw_results = self._service.cse().list(q=query, **query_config).execute().get("items")
        if not raw_results:
            raw_results = pd.DataFrame(columns=_COLUMNS)
        results = _to_result_format(raw_results, query, query_config)
        return results


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
