import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

from tasks.analyze.analyze_text import analyze

st.set_option('deprecation.showPyplotGlobalUse', False)


class StreamlitApp:
    def __init__(self, search_service, scraper):
        self._search_service = search_service
        self._scraper = scraper

    def run(self, base_config):
        config = dict(base_config)
        query = st.sidebar.text_input(label="Zoekopdracht", value="financiële houdbaarheid zorg")
        button = st.sidebar.button(label="Start")
        if button:
            keywords = self._find_keywords(query.lower(), config)
            wordcloud = WordCloud().generate(",".join(keywords))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis("off")
            plt.show()
            st.pyplot(figsize=(500, 250))

    def _find_keywords(self, query: str, config):
        websites = []
        with st.info("...Searching Google for top rankings"):
            for start_idx in (1, 11):
                config["start"] = start_idx
                websites.append(self._search_service.search(query.lower(), config))
        websites = pd.concat(websites, axis=0)
        with st.info("...Scraping website content"):
            texts = [self._scraper.fetch_text(page) for page in websites["link"].values]
        with st.info("...Analyzing top keywords"):
            keywords = analyze(websites, texts)
        return keywords
