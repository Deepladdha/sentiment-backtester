import os
import requests
import pandas as pd
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from backtester.data.base import DataSource
from dotenv import load_dotenv

load_dotenv()

class SentimentDataSource(DataSource):
    def __init__(self):
        self.api_key= os.getenv("NEWS_API_KEY")
        self.analyzer = SentimentIntensityAnalyzer()

    def fetch(self, ticker: str, start: datetime, end: datetime)-> pd.DataFrame:
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

        return pd.DataFrame(records)

