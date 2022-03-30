import miniscule
import pandas as pd

from adapters.factory import create_google_search_service, create_web_scraper
from tasks.analyze.analyze_text import analyze


if __name__ == "__main__":
    config = miniscule.init()
    search_service = create_google_search_service(config)
    scraper = create_web_scraper(config)
    cse_nl = config.get("cse_ids").get("nl")
    websites = []
    for start_idx in (1, 11):
        search_config = {"cx": cse_nl, "num": 10, "start": start_idx}
        websites.append(search_service.search("financiele houdbaarheid ziekenhuiszorg", search_config))
    websites = pd.concat(websites, axis=0)
    texts = [scraper.fetch_text(page) for page in websites["link"].values]
    analyze(websites, texts)
