from decimal import Decimal
from datetime import datetime
import pandas as pd
from backtester.data.cache import Cache


def test_cache_save_and_get(tmp_path):
    cache = Cache(cache_dir=str(tmp_path))
    df = pd.DataFrame({"Close": [Decimal("150.5")], "Volume": [1000]})

    cache.save("AAPL", datetime(2024, 1, 1), datetime(2024, 1, 10), df)
    result = cache.get("AAPL", datetime(2024, 1, 1), datetime(2024, 1, 10))

    assert result is not None
    assert len(result) == 1 

def test_cache_get_returns_none_when_missing(tmp_path):
    cache = Cache(cache_dir=str(tmp_path))
    result = cache.get("MSFT", datetime(2024, 1, 1), datetime(2024, 1, 10))
    assert result is None