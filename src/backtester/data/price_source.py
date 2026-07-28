import yfinance as yf
import pandas as pd
from decimal import Decimal
from datetime import datetime
from backtester.data.base import DataSource
from backtester.data.cache import Cache

class PriceDataSource(DataSource):
    def __init__(self, cache : Cache= None):

    

        self.cache = cache if cache is not None else Cache(cache_dir=".cache/price")

    def fetch(self, ticker:str, start: datetime, end: datetime) -> pd.DataFrame:

        cached_data = self.cache.get(ticker, start, end)
        if cached_data is not None:
            return cached_data.set_index("Date")

        raw_data = yf.download(tickers=ticker, start=start, end=end)
        raw_data.columns = raw_data.columns.get_level_values(0)

        for column in ["Close", "High", "Low", "Open"]:
            raw_data[column] = raw_data[column].apply(lambda x: Decimal(str(round(x,2))))

        self.cache.save(ticker, start, end, raw_data.reset_index())

        return raw_data
        