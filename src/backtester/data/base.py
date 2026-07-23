from abc import ABC, abstractmethod
import pandas as pd
from datetime import datetime


class DataSource(ABC):
    @abstractmethod
    def fetch(self, ticker: str, start: datetime, end: datetime) -> pd.DataFrame:
        ...