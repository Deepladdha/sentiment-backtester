from decimal import Decimal
from datetime import datetime
from backtester.core.transaction import Transaction, Action
from backtester.core.exceptions import InsufficientFundsError, InsufficientHoldingsError
import pytest


def test_buy_reduces_cash(portfolio):
    transaction = Transaction("AAPL", 10, Decimal("150"), datetime.now(), Action.BUY)
    portfolio.execute(transaction)
    assert portfolio.cash == Decimal("8500")

def test_buy_increases_holdings(portfolio):
    transaction = Transaction("AAPL", 10, Decimal("150"), datetime.now(), Action.BUY)
    portfolio.execute(transaction)
    assert portfolio.holdings[transaction.ticker] == 10

def test_sell_increases_cash(portfolio):
    transaction1 = Transaction("AAPL", 10, Decimal("150"), datetime.now(), Action.BUY)
    transaction2 = Transaction("AAPL", 8, Decimal("150"), datetime.now(), Action.SELL)
    portfolio.execute(transaction1)
    portfolio.execute(transaction2)
    assert portfolio.cash == Decimal("9700")

def test_sell_decreases_holdings(portfolio):
    transaction1 = Transaction("AAPL", 10, Decimal("150"), datetime.now(), Action.BUY)
    transaction2 = Transaction("AAPL", 8, Decimal("150"), datetime.now(), Action.SELL)
    portfolio.execute(transaction1)
    portfolio.execute(transaction2)
    assert portfolio.holdings[transaction2.ticker] == 2

def test_buy_raises_insufficientfunds(portfolio):
    transaction = Transaction("AAPL", 1000, Decimal("150"), datetime.now(), Action.BUY)
    with pytest.raises(InsufficientFundsError):
        portfolio.execute(transaction)
def test_sell_raises_insufficientholdings(portfolio):
    transaction = Transaction("AAPL", 10, Decimal("150"), datetime.now(), Action.SELL)
    with pytest.raises(InsufficientHoldingsError):
        portfolio.execute(transaction)

def test_failed_transaction(portfolio):
        transaction = Transaction("AAPL", 10, Decimal("150"), datetime.now(), Action.SELL)
        with pytest.raises(InsufficientHoldingsError):
            portfolio.execute(transaction)
        assert transaction not in portfolio.transaction_history
        
    
