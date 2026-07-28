import pandas as pd
from backtester.strategies.sentiment_threshold import SentimentThresholdStrategy
from backtester.strategies.base import Signal

def test_buy_signal_when_sentiment_above_threshold():
    strategy = SentimentThresholdStrategy(buy_threshold=0.3, sell_threshold=-0.3)
    sentiment_data = pd.DataFrame({"sentiment": [0.1, 0.5]})
    signal = strategy.generate_signal(pd.DataFrame(), sentiment_data)
    assert signal == Signal.BUY

def test_sell_signal_when_sentiment_below_threshold():
    strategy = SentimentThresholdStrategy(buy_threshold=0.5, sell_threshold=-0.5)
    sentiment_data = pd.DataFrame({"sentiment": [-1,-0.6]})
    signal = strategy.generate_signal(pd.DataFrame(), sentiment_data)
    assert signal == Signal.SELL

def test_hold_signal_when_sentiment_between_thresholds():
    strategy = SentimentThresholdStrategy(buy_threshold=0.6, sell_threshold=-0.6)
    sentiment_data = pd.DataFrame({"sentiment": [0.5,-0.5]})
    signal = strategy.generate_signal(pd.DataFrame(), sentiment_data)
    assert signal == Signal.HOLD

def test_hold_signal_when_sentiment_data_empty():
    strategy = SentimentThresholdStrategy(buy_threshold=0.3, sell_threshold= -0.3)
    sentiment_data = pd.DataFrame({"sentiment" : []})   
    signal = strategy.generate_signal(pd.DataFrame(), sentiment_data)
    assert signal == Signal.HOLD         
        

