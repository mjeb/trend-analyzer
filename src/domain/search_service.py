from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict

import pandas as pd


class SearchService(ABC):
    """Abstract search service class defining the underlying methods for searching
    and fetching links to content"""

    @abstractmethod
    def search(self, query: str, query_config: Dict) -> pd.DataFrame:
        """Searches for links found when querying for certain content on a website (or search engine)"""
        pass
