import json

from emporium import Store, create_store, LocalStore

from adapters.cached_google_search import CachedGoogleQueryService
from adapters.web_scraper import WebScraper
from adapters.cached_web_scraper import CachedWebScraper
from adapters.zorgvisie_search import ZorgvisieSearchService


def create_zorgvisie_search_service(config):
    zorgvisie_config = config.get("zorgvisie")
    url = zorgvisie_config.get("url")
    store = create_store(zorgvisie_config, local=LocalStore.from_config)
    return ZorgvisieSearchService(url, store)


def create_google_search_service(config):
    service_config = dict()
    store = create_google_search_store(config)
    credentials_path = config.get("credentials")
    with open(credentials_path, "r") as h:
        credentials = json.load(h)
    service_config["developer_key"] = credentials.get("developer_key")
    service_config["store"] = store
    return CachedGoogleQueryService.from_config(service_config)


def create_google_search_store(config) -> Store:
    store_config = config.get("google_search_store")
    return create_store(store_config, local=LocalStore.from_config)


def create_web_scraper(config):
    store = create_web_scrape_store(config)
    scraper = WebScraper()
    return CachedWebScraper(scraper, store)


def create_web_scrape_store(config) -> Store:
    scrape_store_config = config.get("web_scraper")
    return create_store(scrape_store_config, local=LocalStore.from_config)

