from unittest.mock import patch
from datetime import datetime
import pandas as pd
from decimal import Decimal
from backtester.data.price_source import PriceDataSource

def test_fetch_converts_prices_to_decimal():
    fake_columns = pd.MultiIndex.from_product([['Close', 'High', 'Low', 'Open', 'Volume'], ['AAPL']])
    fake_data = pd.DataFrame(
        [[150.505, 152.0, 149.0, 151.0, 1000000]],
        columns=fake_columns,
        index=pd.to_datetime(['2024-01-02'])
    )
    with patch('backtester.data.price_source.yf.download', return_value=fake_data):
        source= PriceDataSource()
        df = source.fetch("AAPL", datetime(2024, 1, 1), datetime(2024, 1, 10))

    assert df['Close'].iloc[0] == Decimal("150.5")
    assert df['Volume'].dtype == 'int64'