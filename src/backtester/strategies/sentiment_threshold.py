from backtester.strategies.base import Signal
from backtester.strategies.base import Strategy
import pandas as pd
class SentimentThresholdStrategy(Strategy):
    def __init__(self, buy_threshold: float, sell_threshold: float):
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold

    def generate_signal(self, price_data: pd.DataFrame, sentiment_data: pd.DataFrame) -> Signal:
        if sentiment_data.empty:
            return Signal.HOLD

        latest_sentiment = sentiment_data['sentiment'].iloc[-1]

        if latest_sentiment > self.buy_threshold:
            return Signal.BUY
        elif latest_sentiment < self.sell_threshold:
            return Signal.SELL
        else:
            return Signal.HOLD