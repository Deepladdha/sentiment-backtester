import pandas as pd
from backtester.strategies.moving_average_crossover import MovingAverageCrossover
from backtester.strategies.base import Signal

# df = pd.DataFrame({"Close" : [101.0, 102.0, 103.0, 104.0, 0, 300.0, 200.0, 101.0, 10.0, 500.0]},
#                   index = pd.date_range("2026-01-01", periods = 10, freq= "B")
#                   )#period is how many dates to produce after the start date 
# #frequency as B tells to produce dates for only buisness days
def make_price_df(prices):
    return pd.DataFrame(
        {"Close": prices},
        index=pd.date_range("2026-01-01", periods=len(prices), freq="B")
    )


def test_insufficeint_data():
    strategy = MovingAverageCrossover(1 , 10)
    df = make_price_df([100]*10)
    signal = strategy.generate_signal(df, pd.DataFrame())
    assert signal == Signal.HOLD

def test_buy_signal():
    strategy = MovingAverageCrossover(2, 3)
    df = make_price_df([100, 100, 100, 100, 100, 100, 100, 100, 100, 500])
    signal = strategy.generate_signal(df, pd.DataFrame())
    assert signal == Signal.BUY

def test_sell_signal():
    strategy = MovingAverageCrossover(3, 5)
    df = make_price_df([100, 100, 100, 100, 100, 200, 200, 200, 200, 10])
    signal = strategy.generate_signal(df, pd.DataFrame())
    assert signal == Signal.SELL

def test_hold_fast_already_above():
    df = make_price_df([100, 102, 104, 106, 108, 110, 112, 114, 116, 118])  # steady rise
    strategy = MovingAverageCrossover(3, 5)
    signal = strategy.generate_signal(df, pd.DataFrame())
    assert signal == Signal.HOLD

def test_hold_fast_already_below():
    df = make_price_df([200, 198, 196, 194, 192, 190, 188, 186, 184, 182])  # steady fall
    strategy = MovingAverageCrossover(3, 5)
    signal = strategy.generate_signal(df, pd.DataFrame())
    assert signal == Signal.HOLD

def test_hold_when_averages_exactly_equal():
    strategy = MovingAverageCrossover(2, 2)
    df = make_price_df([100] * 10)
    signal = strategy.generate_signal(df, pd.DataFrame())
    assert signal == Signal.HOLD