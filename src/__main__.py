import miniscule

from adapters.factory import create_google_search_service, create_web_scraper, create_zorgvisie_search_service
from app import StreamlitApp

if __name__ == "__main__":
    config = miniscule.init()
    search_service = create_google_search_service(config)
    article_services = [create_zorgvisie_search_service(config), ]
    scraper = create_web_scraper(config)
    cse_nl = config.get("cse_ids").get("nl")
    app = StreamlitApp(search_service, article_services, scraper)
    base_config = {"cx": cse_nl, "num": 10, "start": 1}
    app.run(base_config)
