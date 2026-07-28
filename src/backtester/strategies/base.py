from abc import ABC, abstractmethod
from enum import Enum
import pandas as pd


class Signal(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class Strategy(ABC):
    @abstractmethod
    def generate_signal(self, price_data: pd.DataFrame, sentiment_data: pd.DataFrame) -> Signal:
        ...