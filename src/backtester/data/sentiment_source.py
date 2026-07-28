from backtester.data.cache import Cache
import os
import requests
import pandas as pd
from datetime import datetime
from backtester.data.base import DataSource
from dotenv import load_dotenv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

load_dotenv()

class SentimentDataSource(DataSource):

    def __init__(self, cache : Cache = None):
        self.api_key= os.getenv("NEWS_API_KEY")
        self.analyzer = SentimentIntensityAnalyzer()
        self.cache = cache if cache is not None else Cache(cache_dir=".cache/sentiment")

    def fetch(self, ticker: str, start: datetime, end: datetime)-> pd.DataFrame:

        cached_data = self.cache.get(ticker, start, end)
        if cached_data is not None:
            return cached_data
        response = requests.get("https://newsapi.org/v2/everything",
                            params = {
                                "q" : ticker,
                                "apiKey" : self.api_key,
                                "language" : "en",
                                "from" : start.strftime("%Y-%m-%d"),
                                "to" : end.strftime("%Y-%m-%d")
                                }
                            )
        response.raise_for_status()
        data = response.json()

        records = []
        for article in data["articles"]:
            score = self.analyzer.polarity_scores(article["title"])["compound"]
            records.append({
                "date": article["publishedAt"],
                "ticker" : ticker,
                "headline": article["title"],
                "sentiment": score
                }
            )
        df = pd.DataFrame(records)
        self.cache.save(ticker, start, end, df)

        return df

