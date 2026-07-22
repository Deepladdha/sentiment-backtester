from decimal import Decimal
from backtester.core.transaction import Transaction, Action
from backtester.core.exceptions import InsufficientFundsError, InsufficientHoldingsError

class Portfolio:
    def __init__(self, starting_cash: Decimal):
        self.cash: Decimal = starting_cash
        self.holdings: dict[str, int] = {}
        self.transaction_history: list[Transaction] = []


    def execute(self, transaction: Transaction) -> None:
        if transaction.action == Action.BUY:
            cost = transaction.quantity * transaction.price
            if cost > self.cash:
                raise InsufficientFundsError(
                    f"Not enough cash: need {cost}, have {self.cash}"
                )
            self.cash -= cost
            self.holdings[transaction.ticker] = self.holdings.get(transaction.ticker, 0) + transaction.quantity

        elif transaction.action == Action.SELL:
            current_holding = self.holdings.get(transaction.ticker, 0)
            if transaction.quantity > current_holding:
                raise InsufficientHoldingsError(
                    f"Not enough shares: trying to sell {transaction.quantity}, have {current_holding}"
                )
            proceeds = transaction.quantity * transaction.price
            self.cash += proceeds
            self.holdings[transaction.ticker] -= transaction.quantity

        self.transaction_history.append(transaction)