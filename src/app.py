from typing import List

import pandas as pd
import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt

from tasks.analyze.analyze_text import analyze

st.set_option('deprecation.showPyplotGlobalUse', False)


class StreamlitApp:
    def __init__(self, search_service, article_services, scraper):
        self._search_service = search_service
        self._article_services = article_services
        self._scraper = scraper

    def run(self, base_config):
        config = dict(base_config)
        queries = ["financiële houdbaarheid zorg", ]
        button = st.sidebar.button(label="Start")
        if button:
            keywords = self._find_keywords([q.lower() for q in queries], config)
            wordcloud = WordCloud(max_font_size=50, max_words=10, background_color="white").generate(",".join(keywords))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis("off")
            plt.show()
            st.pyplot(figsize=(500, 250))

    def _find_keywords(self, queries: List[str], config):
        links = []
        with st.spinner("...Searching Google for top rankings"):
            for query in queries:
                for start_idx in (1, 11):
                    config["start"] = start_idx
                    links += self._search_service.search(query, config)
        with st.spinner("...Searching articles in relevant websites"):
            for article_service in self._article_services:
                links += article_service.search()
        st.write(links)
        with st.spinner("...Scraping website content"):
            texts = [self._scraper.fetch_text(link) for link in links]
        with st.spinner("...Analyzing top keywords"):
            keywords = analyze(links, texts)
        return keywords
