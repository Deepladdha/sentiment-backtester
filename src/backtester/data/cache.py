import json
import os
import pandas as pd
from datetime import datetime 

class Cache:
    def __init__(self, cache_dir : str = ".cache"):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def _build_key(self, ticker: str, start: datetime, end: datetime) -> str:
        return f"{ticker}_{start.strftime('%Y-%m-%d')}_{end.strftime('%Y-%m-%d')}"

    def _file_path(self, key: str) -> str:
        return os.path.join(self.cache_dir, f"{key}.json")

    def save(self,ticker: str, start: datetime, end : datetime, df : pd.DataFrame) -> None:
        key = self._build_key(ticker,start,end)
        path = self._file_path(key)
        df.to_json(path, orient="records", date_format= "iso")

    def get(self, ticker: str, start: datetime, end : datetime):
        key = self._build_key(ticker,start,end)
        path = self._file_path(key)
        if not os.path.exists(path):
            return None
        return pd.read_json(path)
        
