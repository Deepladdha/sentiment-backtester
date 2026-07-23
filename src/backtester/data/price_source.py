import yfinance as yf
import pandas as pd
from decimal import Decimal
from datetime import datetime
from backtester.data.base import DataSource

class PriceDataSource(DataSource):
    def fetch(self, ticker:str, start: datetime, end: datetime) -> pd.DataFrame:
        raw_data = yf.download(tickers=ticker, start=start, end=end)
        raw_data.columns = raw_data.columns.get_level_values(0)

        for column in ["Close", "High", "Low", "Open"]:
            raw_data[column] = raw_data[column].apply(lambda x: Decimal(str(round(x,2))))

        return raw_data
        