import pytest
from decimal import Decimal
from backtester.core.portfolio import Portfolio

@pytest.fixture
def portfolio():
    return Portfolio(Decimal("10000"))



