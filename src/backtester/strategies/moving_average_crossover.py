import pandas as pd
from backtester.strategies.base import Strategy, Signal

class MovingAverageCrossover(Strategy) :
    def __init__(self, short_window: int, long_window: int):
        self.short_window = short_window
        self.long_window = long_window

    def generate_signal(self, price_data: pd.DataFrame, sentiment_data: pd.DataFrame):

        if len(price_data) < self.long_window + 1:
            return Signal.HOLD
        
        df = price_data["Close"].astype(float)
        fast_moving_average= df.rolling(window= self.short_window).mean()
        slow_moving_average= df.rolling(window= self.long_window).mean()

        present_fma, present_sma = fast_moving_average.iloc[-1],slow_moving_average.iloc[-1]
        past_fma, past_sma = fast_moving_average.iloc[-2], slow_moving_average.iloc[-2]

        if present_fma > present_sma:
            if past_fma <= past_sma:
                return Signal.BUY
            else:
                return Signal.HOLD
        elif present_fma < present_sma:
            if past_fma >= past_sma:
                return Signal.SELL
            else:
                return Signal.HOLD
        else :
            return Signal.HOLD



        

