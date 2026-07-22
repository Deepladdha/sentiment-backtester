class InsufficientFundsError(Exception):
    """Raised when a portfolio doesn't have enough cash to execute a purchase."""
    pass


class InsufficientHoldingsError(Exception):
    """Raised when a portfolio doesn't own enough shares to execute a sale."""
    pass